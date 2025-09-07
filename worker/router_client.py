import os
from netmiko import ConnectHandler
import ntc_templates


def get_interfaces(ip, username, password):
    """
    เชื่อมต่อไปยัง Router และดึงข้อมูล Interface status.
    """
    # ตั้งค่า TextFSM templates
    os.environ["NET_TEXTFSM"] = os.path.join(
        os.path.dirname(ntc_templates.__file__), "templates"
    )

    device = {
        "device_type": "cisco_ios",  # สมมติว่าเป็น Cisco IOS
        "host": ip,
        "username": username,
        "password": password,
    }

    # ใช้ with-statement เพื่อให้แน่ใจว่าการเชื่อมต่อจะถูกปิดเสมอ
    with ConnectHandler(**device) as conn:
        # รันคำสั่ง และใช้ textfsm แปลงผลลัพธ์เป็น JSON
        result = conn.send_command("show ip interface brief", use_textfsm=True)

    return result
