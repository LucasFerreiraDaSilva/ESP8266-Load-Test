#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>

const char *ssid = "ESP8266";
const char *password = "12345678";

const int bufSize = 1000; // Transfer buffer size, in bytes

WiFiServer server(80);    // Server port

void setup()
{
  Serial.begin(9600);
  Serial.println();

  // Configuring to soft access point mode
  Serial.print("[AP] Setting soft-AP ... ");
  boolean status = WiFi.softAP(ssid, password);
  
  if (status)
    Serial.println("[AP] Access point ready!");
  else
    Serial.println("[AP] Failed to create the access point!");

  // Start the Multicast DNS server
  if (MDNS.begin("esp-8266"))
  {
    Serial.println("[MDNS] Serving: esp-8266.local");
  }

  server.begin();
  server.setNoDelay(true);
}

// Create the HTML page header
String getHTMLHead()
{
  String htmlPage =
    String("HTTP/1.1 200 OK\r\n") +
    "Content-Type: application/octet-stream\r\n" +
    "Content-Length: 999999999999\r\n" +
    "Connection: close\r\n" +
    "\r\n";

  return htmlPage;
}

// Server connection loop
void loop()
{
  WiFiClient client = server.available();
  if (client && client.connected())
  {
    Serial.println("A client found!");
    String line = client.readStringUntil('\n');
    Serial.println(line);
    client.println(getHTMLHead());

    // Data sending loop
    while (client.status())
    {
      byte clientBuf[bufSize];
      client.write((const uint8_t *)clientBuf, bufSize);
    }
    Serial.println("Client stopped!");
  }
}
