import subprocess
import time

def run_script(script_name):
    while True:
        try:
            # Запуск скрипта
            print(f"Запускаем скрипт: {script_name}")
            subprocess.run(['python', script_name], check=True)
        except subprocess.CalledProcessError:
            # Если скрипт завершился с ошибкой
            print(f"Скрипт {script_name} завершился с ошибкой. Перезапуск через 5 секунд...")
            time.sleep(5)  # Ждем 5 секунд перед перезапуском

if __name__ == "__main__":
    script_to_run = "bot_script.py"  # Укажите имя вашего скрипта
    run_script(script_to_run)
