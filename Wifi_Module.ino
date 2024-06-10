#include <ESP8266WiFi.h> // ESP8266 모듈 사용 시

const char* ssid = "Jb";        // WiFi 네트워크 이름
const char* password = "do more ";  // WiFi 비밀번호

const char* host = "192.168.0.18"; // 라즈베리파이 IP 주소
const int port = 5000;             // 라즈베리파이에서 설정한 포트 번호

const int analogPin = A0; // MQ-3 센서가 연결된 아날로그 핀
int initialSensorValue = 0; // 처음 읽은 값을 저장할 변수
bool isInitialRead = true; // 처음 값을 읽었는지 확인하는 변수

void setup() {
  Serial.begin(115200); // 시리얼 통신 초기화
  delay(10);

  // WiFi 연결
  WiFi.begin(ssid, password);

  Serial.print("Connecting to ");
  Serial.print(ssid);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  delay(2000); // 센서 안정화를 위해 초기화 후 잠시 대기
}

void loop() {
  // WiFi 연결 상태 확인
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected, reconnecting...");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    Serial.println("");
    Serial.println("WiFi reconnected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
  }

  int sensorValue = analogRead(analogPin); // MQ-3 센서 값 읽기

  // 처음 값을 읽을 때
  if (isInitialRead) {
    initialSensorValue = sensorValue;
    isInitialRead = false;
  }

  // 현재 값이 처음 값에서 100 이상 떨어졌을 때
  if (initialSensorValue - sensorValue >= 100) {
    Serial.println("Success");
    sendToServer("success");
  }

  Serial.print("MQ-3 sensor value: ");
  Serial.println(sensorValue); // 센서 값을 시리얼 모니터에 출력

  delay(1000); // 1초 대기 후 반복
}

void sendToServer(const char* message) {
  WiFiClient client;

  if (!client.connect(host, port)) {
    Serial.println("Connection to host failed");
    return;
  }

  // 데이터 전송
  client.print(message);
  Serial.println("Data sent to server");

  // 서버로부터 응답 수신
  while (client.available()) {
    String line = client.readStringUntil('\r');
    Serial.print("Received from server: ");
    Serial.println(line);
  }

  client.stop();
}
