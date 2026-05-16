/*
 * Proyecto: Monitoreo de EPP en Área de Torno
 * Dispositivo: Arduino Mega 2560
 * Lógica LED: Verde SOLO cuando hay cumplimiento (OK), Rojo/Buzzer en alerta.
 */

#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Configuración LCD I2C (Dirección 0x27, 16x2)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Pines
const int LED_VERDE = 2;
const int LED_ROJO = 3;
const int BUZZER = 4;

// Timers de control
const unsigned long ALERT_DURATION = 3000;      // 3 seg de alarma activa
const unsigned long COOLDOWN_SERIAL = 2000;     // Mínimo entre mensajes Serial
unsigned long lastAlertTime = 0;
bool alarmaActiva = false;

void setup() {
  Serial.begin(9600);

  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_ROJO, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  // ESTADO INICIAL: Todo apagado (esperando primer comando)
  digitalWrite(LED_VERDE, LOW);
  digitalWrite(LED_ROJO, LOW);
  digitalWrite(BUZZER, LOW);

  lcd.init();
  lcd.backlight();
  mostrarEstadoReposo();
}

void loop() {
  // Procesar mensajes Serial (no bloqueante)
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    procesarComando(comando);
  }

  // Apagar alarma automáticamente después de ALERT_DURATION
  if (alarmaActiva && (millis() - lastAlertTime > ALERT_DURATION)) {
    desactivarAlarma();
  }
}

void procesarComando(String cmd) {
  if (cmd == "OK") {
    ejecutarAccesoConcedido();
  } 
  else if (cmd.startsWith("FALTA:")) {
    String items = cmd.substring(6);  // Extraer "Casco, Chaleco"
    ejecutarAlarma(items);
  }
}

void mostrarEstadoReposo() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("SISTEMA EPP");
  lcd.setCursor(0, 1);
  lcd.print("ESPERANDO...");
}

void ejecutarAccesoConcedido() {
  // Si recibimos OK, el cumplimiento está restaurado: forzar estado verde
  alarmaActiva = false;
  
  digitalWrite(LED_VERDE, HIGH);   // ✅ ENCENDER VERDE
  digitalWrite(LED_ROJO, LOW);     // ❌ APAGAR ROJO
  digitalWrite(BUZZER, LOW);       // 🔇 APAGAR BUZZER

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("EPP CORRECTO");
  lcd.setCursor(0, 1);
  lcd.print("CASCO + CHALECO");
}

void ejecutarAlarma(String itemsFaltantes) {
  // Evitar rebotes por saturación de mensajes
  if (alarmaActiva || (millis() - lastAlertTime < COOLDOWN_SERIAL)) {
    return;
  }

  alarmaActiva = true;
  lastAlertTime = millis();

  //  APAGAR VERDE, ENCENDER ROJO Y BUZZER
  digitalWrite(LED_VERDE, LOW);
  digitalWrite(LED_ROJO, HIGH);
  tonoAlarma();

  // Mostrar en LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("ALERTA EPP!");
  lcd.setCursor(0, 1);
  
  // Ajuste automático para LCD 16x2
  if (itemsFaltantes.length() <= 16) {
    lcd.print(itemsFaltantes);
  } else {
    int corte = itemsFaltantes.indexOf(',', 8);
    if (corte > 0 && corte < 16) {
      lcd.print(itemsFaltantes.substring(0, corte));
    } else {
      lcd.print(itemsFaltantes.substring(0, 13) + "...");
    }
  }
}

void desactivarAlarma() {
  alarmaActiva = false;
  digitalWrite(LED_ROJO, LOW);
  digitalWrite(BUZZER, LOW);
  
  // ⚠️ IMPORTANTE: El verde NO se enciende aquí automáticamente.
  // Permanece apagado hasta que Python envíe "OK" confirmando cumplimiento.
  mostrarEstadoReposo();
}

void tonoAlarma() {
  // Patrón de buzzer: 3 pulsos cortos
  for (int i = 0; i < 3; i++) {
    digitalWrite(BUZZER, HIGH);
    delay(100);
    digitalWrite(BUZZER, LOW);
    delay(100);
  }
}