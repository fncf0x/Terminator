import sqlite3
import os


class TerminatorDB:
    def __init__(self, db_path):
        self.port_count = os.getenv("PORT_COUNT", 16)
        self.hub_count = os.getenv("HUB_COUNT", 2)
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS proxies (id INTEGER PRIMARY KEY AUTOINCREMENT, usb_port text, interface text, local_ip text, public_ip text, status text)
        """)
        self.cursor = self.conn.cursor()
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
        rows = self.cursor.execute(f"SELECT local_ip, interface FROM proxies WHERE status='plugged' OR status='up'").fetchall()
        return [row for row in rows]

    def get_iface_ip(self, interface):
        rows = self.cursor.execute(f"SELECT local_ip FROM proxies WHERE interface='{interface}'").fetchall()
        return rows[0][0]

    def get_all_ports(self):
        rows = self.cursor.execute(f"SELECT usb_port, interface, local_ip, status FROM proxies").fetchall()
        return [row for row in rows]

    def check_if_iface_exist(self, name):
        rows = self.cursor.execute(f"SELECT id FROM proxies WHERE interface='{name}'").fetchall()
        return bool(len(rows))

    def check_if_port_exist(self, port):
        rows = self.cursor.execute(f"SELECT id FROM proxies WHERE usb_port='{port}'").fetchall()
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


