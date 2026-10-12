#include <Mouse.h>

#define BAUD      115200
#define TIMEOUT   500
#define BUF_SIZE  32

char     buf[BUF_SIZE];
uint8_t  idx      = 0;
uint32_t lastRecv = 0;

void setup() {
  Serial.begin(BAUD);
  Mouse.begin();
}

void loop() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    lastRecv = millis();

    if (c == '\n') {
      buf[idx] = '\0';
      idx = 0;

      char *comma = strchr(buf, ',');
      if (comma) {
        *comma = '\0';
        int dx = atoi(buf);
        int dy = atoi(comma + 1);
        if (dx != 0 || dy != 0) {
          Mouse.move(dx, dy, 0);
        }
      }
    } else {
      if (idx < BUF_SIZE - 1) buf[idx++] = c;
    }
  }

  if (millis() - lastRecv > TIMEOUT) {
    lastRecv = millis();
  }
}
