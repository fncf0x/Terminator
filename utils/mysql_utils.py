import os
import mysql.connector


class TerminatorDB:
    def __init__(self, username, password):
        self.port_count = os.getenv("PORT_COUNT", 16)
        self.hub_count = os.getenv("HUB_COUNT", 2)
        self.conn = mysql.connector.connect(user=username, password=password, host='localhost', database='terminator', auth_plugin='mysql_native_password')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS proxies (id INTEGER PRIMARY KEY AUTO_INCREMENT, usb_port varchar(10), interface varchar(30), local_ip varchar(20), public_ip varchar(20), status varchar(20))
        """)
        for hub in range(self.hub_count):
            hub_num = hub + 1
            for port in range(self.port_count):
                port_number = port + 1
                usb_port = f"{hub_num}_{str(port_number).zfill(2)}"
                if self.check_if_port_exist(usb_port):
                    continue
                self.cursor.execute(f"INSERT INTO proxies(usb_port, status) VALUES('{usb_port}', 'empty')")
        self.conn.commit()

    def get_up_proxies(self):
        self.cursor.execute(f"SELECT local_ip, interface FROM proxies WHERE status='plugged' OR status='up'")
        rows = self.cursor.fetchall()
        self.conn.commit()
        return [row for row in rows]

    def get_iface_ip(self, interface):
        self.cursor.execute(f"SELECT local_ip FROM proxies WHERE interface='{interface}'")
        rows = self.cursor.fetchall()
        self.conn.commit()
        return rows[0][0]

    def get_all_ports(self):
        self.cursor.execute(f"SELECT usb_port, interface, local_ip, status FROM proxies")
        rows = self.cursor.fetchall()
        self.conn.commit()
        return [row for row in rows]

    def check_if_iface_exist(self, name):
        self.cursor.execute(f"SELECT id FROM proxies WHERE interface='{name}'")
        rows = self.cursor.fetchall()
        self.conn.commit()
        return bool(len(rows))

    def check_if_port_exist(self, port):
        self.cursor.execute(f"SELECT id FROM proxies WHERE usb_port='{port}'")
        rows = self.cursor.fetchall()
        self.conn.commit()
        return bool(len(rows))

    def update_interface_infos(self, port, name, ip, status, public_ip=""):
        if not self.check_if_port_exist(port):
            self.add_interface(port)

        self.cursor.execute(f'UPDATE proxies SET local_ip="{ip}", interface="{name}", status="{status}", public_ip="{public_ip}" WHERE usb_port="{port}"')
        self.conn.commit()

    def clean_port(self, name):
        if not self.check_if_iface_exist(name):
            return
        self.cursor.execute(f'UPDATE proxies SET local_ip="", interface="", public_ip="", status="empty" WHERE interface="{name}"')
        self.conn.commit()

    def add_interface(self, port):
        self.cursor.execute(f"INSERT INTO proxies(usb_port) VALUES('{port}')")
        self.conn.commit()

    def __exit__(self):
        self.conn.close()


