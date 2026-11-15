using System;
using System.Collections.Generic;
using System.Linq;
using Windows.Data.Json;
using Windows.UI.Notifications;
using Windows.UI.Notifications.Management;
using Windows.UI.Xaml;
using Windows.UI.Xaml.Controls;
using Windows.Web.Http;

namespace BalaJarvisWindowsBridge
{
    public sealed partial class MainPage : Page
    {
        private readonly UserNotificationListener listener = UserNotificationListener.Current;
        private readonly DispatcherTimer timer = new DispatcherTimer();
        private readonly HashSet<uint> sentIds = new HashSet<uint>();
        private bool running = false;

        public MainPage()
        {
            InitializeComponent();
            timer.Interval = TimeSpan.FromSeconds(2);
            timer.Tick += Timer_Tick;
        }

        private async void GrantButton_Click(object sender, RoutedEventArgs e)
        {
            GrantButton.IsEnabled = false;
            try
            {
                var access = await listener.RequestAccessAsync();
                if (access == UserNotificationListenerAccessStatus.Allowed)
                {
                    StatusText.Text = "Permission granted. Monitoring supported app notifications while this window remains open.";
                    running = true;
                    timer.Start();
                    await ScanNotificationsAsync();
                }
                else
                {
                    StatusText.Text = "Notification access was not granted. You can enable it later in Windows Settings.";
                }
            }
            catch (Exception ex)
            {
                StatusText.Text = "Could not start notification access: " + ex.Message;
            }
            finally { GrantButton.IsEnabled = true; }
        }

        private async void Timer_Tick(object sender, object e)
        {
            if (running) await ScanNotificationsAsync();
        }

        private async System.Threading.Tasks.Task ScanNotificationsAsync()
        {
            try
            {
                var notifications = await listener.GetNotificationsAsync(NotificationKinds.Toast);
                foreach (var item in notifications)
                {
                    if (sentIds.Contains(item.Id)) continue;
                    if (item.CreationTime < DateTimeOffset.Now.AddMinutes(-2)) continue;
                    var appName = item.AppInfo?.DisplayInfo?.DisplayName ?? item.AppInfo?.Id ?? "Windows app";
                    var appId = item.AppInfo?.Id ?? "";
                    var appIdentity = (appName + " " + appId).ToLowerInvariant();

                    string sourceApp = null;
                    if (appIdentity.Contains("phone link") || appIdentity.Contains("yourphone") || appIdentity.Contains("your phone"))
                        sourceApp = "Phone Link";
                    else if (appIdentity.Contains("whatsapp"))
                        sourceApp = "WhatsApp Desktop";
                    else if (appIdentity.Contains("teams") || appIdentity.Contains("msteams"))
                        sourceApp = "Microsoft Teams";
                    if (sourceApp == null) continue;

                    var binding = item.Notification?.Visual?.GetBinding(KnownNotificationBindings.ToastGeneric);
                    if (binding == null) continue;
                    var text = string.Join(" ", binding.GetTextElements().Select(t => t.Text).Where(t => !string.IsNullOrWhiteSpace(t)));
                    if (string.IsNullOrWhiteSpace(text)) continue;
                    var lower = text.ToLowerInvariant();
                    bool callLike = new[] { "incoming call", "is calling", "calling you", "voice call", "video call", "call from", "incoming audio", "incoming video" }.Any(k => lower.Contains(k));
                    if (!callLike) continue;

                    sentIds.Add(item.Id);
                    if (sentIds.Count > 500) sentIds.Clear();
                    await ForwardCallAsync(sourceApp, text);
                }
            }
            catch (Exception ex)
            {
                StatusText.Text = "Monitoring paused: " + ex.Message;
            }
        }

        private async System.Threading.Tasks.Task ForwardCallAsync(string app, string notificationText)
        {
            try
            {
                var payload = new JsonObject
                {
                    ["source"] = JsonValue.CreateStringValue("windows"),
                    ["kind"] = JsonValue.CreateStringValue("call"),
                    ["title"] = JsonValue.CreateStringValue("Incoming call notification"),
                    ["detail"] = JsonValue.CreateStringValue(notificationText.Length > 240 ? notificationText.Substring(0, 240) : notificationText),
                    ["app"] = JsonValue.CreateStringValue(app)
                };
                using (var client = new HttpClient())
                using (var content = new HttpStringContent(payload.ToString(), Windows.Storage.Streams.UnicodeEncoding.Utf8, "application/json"))
                {
                    var response = await client.PostAsync(new Uri("http://127.0.0.1:8000/api/notifications"), content);
                    StatusText.Text = response.IsSuccessStatusCode
                        ? "Connected · " + app + " call alert forwarded to BALA JARVIS."
                        : "Jarvis server returned " + (int)response.StatusCode + ". Keep jarvis_server.py running.";
                }
            }
            catch
            {
                StatusText.Text = "Cannot reach BALA JARVIS at 127.0.0.1:8000. Start jarvis_server.py first.";
            }
        }
    }
}
