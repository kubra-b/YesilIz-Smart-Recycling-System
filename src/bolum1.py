import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QStackedWidget, 
                             QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QFormLayout, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont,QCursor

# Matplotlib entegrasyonu (Grafikler için)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Yazdığımız veritabanı dosyasını içe aktarıyoruz
import databasekod as db

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.setStyleSheet("""
            ModernButton {
                background-color: #10B981 !important;
                color: white !important;
                border-radius: 8px;
                padding: 10px 15px;
                border: none;
            }
            ModernButton:hover {
                background-color: #059669 !important;
            }
        """)

class YesilIzApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yeşilİz - Akıllı Geri Dönüşüm Sistemi")
        self.setGeometry(100, 100, 1000, 700) # Profesyonel bir pencere boyutu
        
        # Aktif kullanıcı bilgilerini tutmak için değişkenler
        self.current_user_id = None
        self.is_admin_mode = False

        # Veritabanını kontrol et/oluştur
        db.create_database()

        # Ana Stacked Widget (Ekranlar arası geçiş köprüsü)
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 6 Ekranın oluşturulması
        self.ekran_giris = QWidget()
        self.ekran_kayit = QWidget()
        self.ekran_dashboard = QWidget()
        self.ekran_grafikler = QWidget()
        self.ekran_liderlik = QWidget()
        self.ekran_etkinlikler = QWidget()
        self.ekran_admin = QWidget()

        # Ekranları Stacked Widget'a ekleme
        self.stacked_widget.addWidget(self.ekran_giris)      # İndeks 0
        self.stacked_widget.addWidget(self.ekran_kayit)      # İndeks 1
        self.stacked_widget.addWidget(self.ekran_dashboard)  # İndeks 2
        self.stacked_widget.addWidget(self.ekran_grafikler)  # İndeks 3
        self.stacked_widget.addWidget(self.ekran_liderlik)   # İndeks 4
        self.stacked_widget.addWidget(self.ekran_etkinlikler) # İndeks 5
        self.stacked_widget.addWidget(self.ekran_admin)      # İndeks 6

        # Ekran tasarımlarını başlat
        self.tasarla_giris()
        self.tasarla_kayit()
        
        # Genel CSS Stil Sayfası (Profesyonel Yeşil Tema)
        self.setStyleSheet("""
            QMainWindow { background-color: #F4F7F6; }
            QLabel { color: #2C3E50; }
            QLineEdit { 
                border: 2px solid #BDC3C7; 
                border-radius: 8px; 
                padding: 8px; 
                background-color: white; 
                font-size: 11pt;
            }
            QLineEdit:focus { border: 2px solid #2ECC71; }
            QPushButton { 
                background-color: #2ECC71; 
                color: white; 
                border-radius: 8px; 
                padding: 5px;
            }
            QPushButton:hover { background-color: #27AE60; }
            QTableWidget { 
                background-color: white; 
                border: 1px solid #BDC3C7; 
                border-radius: 8px; 
            }
            QComboBox {
                border: 2px solid #BDC3C7;
                border-radius: 8px;
                padding: 5px;
                min-height: 30px;
            }
        """)

    # ----------------------------------------------------
    # EKRAN 1: GİRİŞ EKRANI TASARIMI
    # ----------------------------------------------------
    def tasarla_giris(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Logo / Başlık Alanı
        lbl_baslik = QLabel("Yeşilİz'e Hoş Geldiniz")
        lbl_baslik.setFont(QFont("Arial", 24, QFont.Bold))
        lbl_baslik.setStyleSheet("color: #27AE60; margin-bottom: 20px;")
        layout.addWidget(lbl_baslik, alignment=Qt.AlignCenter)

        # Form Alanı
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 12px; padding: 20px;")
        form_frame.setFixedWidth(380)
        form_layout = QFormLayout(form_frame)

        self.txt_giris_username = QLineEdit()
        self.txt_giris_password = QLineEdit()
        self.txt_giris_password.setEchoMode(QLineEdit.Password)

        form_layout.addRow(QLabel("Kullanıcı Adı:"), self.txt_giris_username)
        form_layout.addRow(QLabel("Şifre:"), self.txt_giris_password)

        layout.addWidget(form_frame, alignment=Qt.AlignCenter)

        # Butonlar
        btn_giris = ModernButton("Giriş Yap")
        btn_giris.clicked.connect(self.islem_giris)
        layout.addWidget(btn_giris, alignment=Qt.AlignCenter)
        btn_giris.setFixedWidth(380)

        btn_admin_giris = ModernButton("Yönetici Olarak Giriş Yap")
        btn_admin_giris.setStyleSheet("background-color: #34495E;")
        btn_admin_giris.clicked.connect(lambda: self.islem_giris(is_admin=True))
        layout.addWidget(btn_admin_giris, alignment=Qt.AlignCenter)
        btn_admin_giris.setFixedWidth(380)

        btn_git_kayit = QPushButton("Hesabınız yok mu? Kaydolun")
        btn_git_kayit.setStyleSheet("background: none; color: #2980B9; border: none; font-size: 10pt;")
        btn_git_kayit.setCursor(Qt.PointingHandCursor)
        btn_git_kayit.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(btn_git_kayit, alignment=Qt.AlignCenter)

        self.ekran_giris.setLayout(layout)

    def islem_giris(self, is_admin=False):
        username = self.txt_giris_username.text()
        password = self.txt_giris_password.text()

        # Terminalden ne yazıldığını kontrol etmek için (Hata ayıklama logu)
        print(f"Giriş deneniyor -> Kullanıcı: {username}, Şifre: {password}, Admin mi: {is_admin}")

        try:
            user_id = db.check_login(username, password, is_admin)
            print(f"Veritabanı dönüşü (ID): {user_id}")
            
            if user_id is not None:
                self.current_user_id = user_id
                self.is_admin_mode = is_admin
                
                if is_admin:
                    self.tasarla_admin()
                    self.stacked_widget.setCurrentIndex(6) # Admin ekranına git
                else:
                    self.tasarla_dashboard()
                    self.stacked_widget.setCurrentIndex(2) # Dashboard'a git
            else:
                QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre hatalı!")
        except Exception as e:
            print(f"Sistemsel Giriş Hatası: {e}")
            QMessageBox.critical(self, "Sistem Hatası", f"Veritabanı bağlantı hatası: {e}")
    # ----------------------------------------------------
    # EKRAN 2: KAYIT EKRANI TASARIMI
    # ----------------------------------------------------
    def tasarla_kayit(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        lbl_baslik = QLabel("Yeşilİz Kayıt Paneli")
        lbl_baslik.setFont(QFont("Arial", 20, QFont.Bold))
        lbl_baslik.setStyleSheet("color: #27AE60; margin-bottom: 20px;")
        layout.addWidget(lbl_baslik, alignment=Qt.AlignCenter)

        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 12px; padding: 20px;")
        form_frame.setFixedWidth(380)
        form_layout = QFormLayout(form_frame)

        self.txt_kayit_ad = QLineEdit()
        self.txt_kayit_username = QLineEdit()
        self.txt_kayit_email = QLineEdit()
        self.txt_kayit_password = QLineEdit()
        self.txt_kayit_password.setEchoMode(QLineEdit.Password)

        form_layout.addRow(QLabel("Ad Soyad:"), self.txt_kayit_ad)
        form_layout.addRow(QLabel("Kullanıcı Adı:"), self.txt_kayit_username)
        form_layout.addRow(QLabel("E-posta:"), self.txt_kayit_email)
        form_layout.addRow(QLabel("Şifre:"), self.txt_kayit_password)

        layout.addWidget(form_frame, alignment=Qt.AlignCenter)

        btn_kayit = ModernButton("Kayıt Ol")
        btn_kayit.clicked.connect(self.islem_kayit)
        layout.addWidget(btn_kayit, alignment=Qt.AlignCenter)
        btn_kayit.setFixedWidth(380)

        btn_git_giris = QPushButton("Zaten hesabınız var mı? Giriş yapın")
        btn_git_giris.setStyleSheet("background: none; color: #2980B9; border: none;")
        btn_git_giris.setCursor(Qt.PointingHandCursor)
        btn_git_giris.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(btn_git_giris, alignment=Qt.AlignCenter)

        self.ekran_kayit.setLayout(layout)

    def islem_kayit(self):
        ad = self.txt_kayit_ad.text()
        user = self.txt_kayit_username.text()
        mail = self.txt_kayit_email.text()
        sifre = self.txt_kayit_password.text()

        if ad and user and mail and sifre:
            if db.user_register(ad, user, mail, sifre):
                QMessageBox.information(self, "Başarılı", "Kaydınız başarıyla oluşturuldu! Giriş yapabilirsiniz.")
                self.stacked_widget.setCurrentIndex(0)
            else:
                QMessageBox.warning(self, "Hata", "Kullanıcı adı veya E-posta sistemde zaten mevcut!")
        else:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun!")

    # ----------------------------------------------------
    # YARDIMCI MENÜ: SOL TARAF NAVİGASYON BARI
    # ----------------------------------------------------
    def sol_menu_olustur(self):
        """Kullanıcı ekranlarında sol tarafta sabit duracak menü barı"""
        sol_panel = QFrame()
        sol_panel.setFixedWidth(200)
        sol_panel.setStyleSheet("background-color: #2C3E50; border-radius: 0px;")
        
        layout = QVBoxLayout(sol_panel)
        layout.setContentsMargins(10, 30, 10, 10)
        
        lbl_logo = QLabel("Yeşilİz")
        lbl_logo.setFont(QFont("Arial", 18, QFont.Bold))
        lbl_logo.setStyleSheet("color: #2ECC71; margin-bottom: 30px;")
        layout.addWidget(lbl_logo, alignment=Qt.AlignCenter)

        btn_dash = QPushButton("Ana Panel")
        btn_grafik = QPushButton("Grafikler")
        btn_lider = QPushButton("Liderlik Tablosu")
        btn_etk = QPushButton("Etkinlik & Noktalar")
        btn_cikis = QPushButton("Çıkış Yap")

        menu_butonlar = [btn_dash, btn_grafik, btn_lider, btn_etk, btn_cikis]
        for btn in menu_butonlar:
            btn.setFont(QFont("Arial", 10, QFont.Bold))
            btn.setMinimumHeight(45)
            btn.setCursor(Qt.PointingHandCursor)
            if btn == btn_cikis:
                btn.setStyleSheet("background-color: #E74C3C; color: white; border:none; border-radius: 5px;")
            else:
                btn.setStyleSheet("background-color: transparent; color: #ECF0F1; text-align: left; padding-left: 15px; border:none;")
            layout.addWidget(btn)
        
        # Menü yönlendirmeleri
        btn_dash.clicked.connect(self.yenile_ve_dashboard_git)
        btn_grafik.clicked.connect(self.tasarla_grafikler)
        btn_lider.clicked.connect(self.tasarla_liderlik)
        btn_etk.clicked.connect(self.tasarla_etkinlikler)
        btn_cikis.clicked.connect(self.islem_cikis)

        layout.addStretch() # Elemanları yukarı yasla
        return sol_panel

    def islem_cikis(self):
        self.current_user_id = None
        self.stacked_widget.setCurrentIndex(0)

    def yenile_ve_dashboard_git(self):
        self.tasarla_dashboard()
        self.stacked_widget.setCurrentIndex(2)

    # ----------------------------------------------------
    # EKRAN 3: DASHBOARD (ANA PANEL) - HATA KORUMALI
    # ----------------------------------------------------
    def tasarla_dashboard(self):
        try:
            # Eğer sayfa daha önce düzenlendiyse eski layout'u temizle
            if self.ekran_dashboard.layout():
                QWidget().setLayout(self.ekran_dashboard.layout())

            ana_layout = QHBoxLayout()
            ana_layout.setContentsMargins(0, 0, 0, 0)
            
            # 1. Sol Menüyü Ekle
            ana_layout.addWidget(self.sol_menu_olustur())

            # 2. Sağ İçerik Alanı
            sag_icerik = QWidget()
            sag_layout = QVBoxLayout(sag_icerik)
            sag_layout.setContentsMargins(20, 20, 20, 20)

            # Veritabanından verileri çekelim
            ad_soyad, tohum_puan, fidan_sayisi = db.get_user_stats(self.current_user_id)

            # Karşılama Alanı
            lbl_welcome = QLabel(f"Merhaba, {ad_soyad}")
            lbl_welcome.setFont(QFont("Arial", 18, QFont.Bold))
            sag_layout.addWidget(lbl_welcome)

            # İstatistik Kartları (Yan Yana)
            kartlar_layout = QHBoxLayout()
            
            kart_tohum = QFrame()
            kart_tohum.setStyleSheet("background-color: #E8F8F5; border-radius: 10px; padding: 15px;")
            kt_lay = QVBoxLayout(kart_tohum)
            kt_lay.addWidget(QLabel("Mevcut Tohum Puanı"), alignment=Qt.AlignCenter)
            lbl_tp = QLabel(str(tohum_puan))
            lbl_tp.setFont(QFont("Arial", 20, QFont.Bold))
            lbl_tp.setStyleSheet("color: #117A65;")
            kt_lay.addWidget(lbl_tp, alignment=Qt.AlignCenter)

            kart_fidan = QFrame()
            kart_fidan.setStyleSheet("background-color: #EAF2F8; border-radius: 10px; padding: 15px;")
            kf_lay = QVBoxLayout(kart_fidan)
            kf_lay.addWidget(QLabel("Adınıza Dikilen Fidan"), alignment=Qt.AlignCenter)
            lbl_fs = QLabel(str(fidan_sayisi))
            lbl_fs.setFont(QFont("Arial", 20, QFont.Bold))
            lbl_fs.setStyleSheet("color: #2471A3;")
            kf_lay.addWidget(lbl_fs, alignment=Qt.AlignCenter)

            kartlar_layout.addWidget(kart_tohum)
            kartlar_layout.addWidget(kart_fidan)
            sag_layout.addLayout(kartlar_layout)

            # Atık Giriş Formu
            sag_layout.addWidget(QLabel("ーーー Yeni Geri Dönüşüm Girişi Yap ーーー"))
            
            form_frame = QFrame()
            form_frame.setStyleSheet("background-color: white; border-radius: 10px; padding: 15px;")
            form_ic_layout = QVBoxLayout(form_frame)

            form_lay = QFormLayout()
            self.cmb_atik_turu = QComboBox()
            self.cmb_atik_turu.addItems(["Plastik", "Kağıt", "Cam", "Metal", "Elektronik"])
            
            self.txt_miktar = QLineEdit()
            self.txt_miktar.setPlaceholderText("Miktar girin (kg)")

            form_lay.addRow(QLabel("Atık Türü:"), self.cmb_atik_turu)
            form_lay.addRow(QLabel("Miktar (kg):"), self.txt_miktar)
            form_ic_layout.addLayout(form_lay)

            btn_atik_ekle = ModernButton("Geri Dönüştür ve Tohum Kazan!")
            btn_atik_ekle.setStyleSheet("background-color: #27AE60; color: white; min-height: 40px;")
            btn_atik_ekle.clicked.connect(self.islem_atik_ekle)
            form_ic_layout.addWidget(btn_atik_ekle)

            sag_layout.addWidget(form_frame)
            sag_layout.addStretch()

            ana_layout.addWidget(sag_icerik)
            self.ekran_dashboard.setLayout(ana_layout)
            
        except Exception as e:
            print(f"DASHBOARD ÇİZİM HATASI: {e}")
            QMessageBox.critical(self, "Arayüz Hatası", f"Dashboard yüklenirken hata oluştu: {e}")

    def islem_atik_ekle(self):
        try:
            miktar = float(self.txt_miktar.text())
            turu = self.cmb_atik_turu.currentText()
            if miktar <= 0:
                raise ValueError
            
            puan, karbon = db.add_recycling_activity(self.current_user_id, turu, miktar)
            QMessageBox.information(self, "Tebrikler!", f"Atık başarıyla işlendi!\nKazanılan Tohum: {puan}\nSağlanan Karbon Tasarrufu: {karbon} kg CO2")
            self.tasarla_dashboard() # Ekranı yenile
        except ValueError:
            QMessageBox.warning(self, "Hata", "Lütfen geçerli (pozitif) bir miktar girin!")
            # ----------------------------------------------------
    # EKRAN 4: GRAFİKLER VE ANALİZ EKRANI
    # ----------------------------------------------------
    # ----------------------------------------------------
    # EKRAN 4: GRAFİKLER VE ANALİZ EKRANI (FULL SÜRÜM)
    # ----------------------------------------------------
    def tasarla_grafikler(self):
        if self.ekran_grafikler.layout():
            QWidget().setLayout(self.ekran_grafikler.layout())

        ana_layout = QHBoxLayout()
        ana_layout.setContentsMargins(0, 0, 0, 0)
        ana_layout.addWidget(self.sol_menu_olustur())

        sag_icerik = QWidget()
        sag_layout = QVBoxLayout(sag_icerik)

        lbl_baslik = QLabel("Geri Dönüşüm Analiz Grafikleriniz")
        lbl_baslik.setFont(QFont("Arial", 16, QFont.Bold))
        sag_layout.addWidget(lbl_baslik)

        # Matplotlib Grafik Alanı (Yan yana iki grafik için layout)
        grafik_layout = QHBoxLayout()

        # 1. Pasta Grafiği (Atık Türü Dağılımı)
        fig_pasta = Figure(figsize=(4, 4), dpi=100)
        canvas_pasta = FigureCanvas(fig_pasta)
        ax_pasta = fig_pasta.add_subplot(111)
        
        pasta_verisi = db.sqlite3.connect(db.DB_PATH).cursor().execute(
            "SELECT atik_turu, SUM(miktar) FROM recycling WHERE user_id = ? GROUP BY atik_turu", 
            (self.current_user_id,)
        ).fetchall()

        if pasta_verisi:
            etiketler = [v[0] for v in pasta_verisi]
            miktarlar = [v[1] for v in pasta_verisi]
            ax_pasta.pie(miktarlar, labels=etiketler, autopct='%1.1f%%', colors=['#2ECC71', '#3498DB', '#F1C40F', '#E74C3C', '#9B59B6'])
            ax_pasta.set_title("Atık Türü Dağılımı (kg)")
        else:
            ax_pasta.text(0.5, 0.5, 'Henüz veri yok', ha='center', va='center')

        # 2. Çizgi Grafiği (İşlem Sırasına Göre Miktar Değişimi)
        fig_cizgi = Figure(figsize=(4, 4), dpi=100)
        canvas_cizgi = FigureCanvas(fig_cizgi)
        ax_cizgi = fig_cizgi.add_subplot(111)

        cizgi_verisi = db.sqlite3.connect(db.DB_PATH).cursor().execute(
            "SELECT miktar FROM recycling WHERE user_id = ? ORDER BY id ASC", 
            (self.current_user_id,)
        ).fetchall()

        if cizgi_verisi:
            islem_numaralari = [f"{i+1}.İşlem" for i in range(len(cizgi_verisi))]
            miktarlar = [v[0] for v in cizgi_verisi]
            
            ax_cizgi.plot(islem_numaralari, miktarlar, marker='o', linestyle='-', color='#27AE60', linewidth=2, markersize=6)
            ax_cizgi.set_title("Geri Dönüşüm Miktar Trendi")
            ax_cizgi.set_ylabel("Miktar (kg)")
            ax_cizgi.grid(True, linestyle='--', alpha=0.6)
            fig_cizgi.autofmt_xdate(rotation=30)
        else:
            ax_cizgi.text(0.5, 0.5, 'Henüz veri yok', ha='center', va='center')

        grafik_layout.addWidget(canvas_pasta)
        grafik_layout.addWidget(canvas_cizgi)
        sag_layout.addLayout(grafik_layout)

        # Karbon Tasarrufu Göstergesi
        toplam_karbon = db.sqlite3.connect(db.DB_PATH).cursor().execute(
            "SELECT SUM(karbon_tasarrufu) FROM recycling WHERE user_id = ?", (self.current_user_id,)
        ).fetchone()[0]
        toplam_karbon = round(toplam_karbon, 2) if toplam_karbon else 0.0

        kart_karbon = QFrame()
        kart_karbon.setStyleSheet("background-color: #D5F5E3; border-radius: 10px; padding: 15px; margin-top: 10px;")
        karbon_lay = QVBoxLayout(kart_karbon)
        lbl_karbon_text = QLabel(f"🌱 Toplam Engellenen Karbon Salınımı: {toplam_karbon} kg CO₂")
        lbl_karbon_text.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_karbon_text.setStyleSheet("color : #1E8449;")
        karbon_lay.addWidget(lbl_karbon_text, alignment=Qt.AlignCenter)
        
        sag_layout.addWidget(kart_karbon)
        ana_layout.addWidget(sag_icerik)
        self.ekran_grafikler.setLayout(ana_layout)
        self.stacked_widget.setCurrentIndex(3)
    # ----------------------------------------------------
    # EKRAN 5: LİDERLİK TABLOSU
    # ----------------------------------------------------
    def tasarla_liderlik(self):
        if self.ekran_liderlik.layout():
            QWidget().setLayout(self.ekran_liderlik.layout())

        ana_layout = QHBoxLayout()
        ana_layout.setContentsMargins(0, 0, 0, 0)
        ana_layout.addWidget(self.sol_menu_olustur())

        sag_icerik = QWidget()
        sag_layout = QVBoxLayout(sag_icerik)

        lbl_baslik = QLabel("🏆 Yeşilİz Liderlik Tablosu (En İyiler)")
        lbl_baslik.setFont(QFont("Arial", 16, QFont.Bold))
        sag_layout.addWidget(lbl_baslik)

        # Tablo Oluşturma
        tablo = QTableWidget()
        tablo.setColumnCount(4)
        tablo.setHorizontalHeaderLabels(["Sıra", "Kullanıcı Adı", "Dikilen Fidan", "Tohum Puanı"])
        tablo.horizontalHeader().setStretchLastSection(True)

        liderler = db.get_leaderboard()
        tablo.setRowCount(len(liderler))

        for sira, veri in enumerate(liderler):
            tablo.setItem(sira, 0, QTableWidgetItem(f"{sira + 1}."))
            tablo.setItem(sira, 1, QTableWidgetItem(str(veri[0])))
            tablo.setItem(sira, 2, QTableWidgetItem(f"🌲 {veri[1]} Fidan"))
            tablo.setItem(sira, 3, QTableWidgetItem(f"✨ {veri[2]} Puan"))

        sag_layout.addWidget(tablo)
        ana_layout.addWidget(sag_icerik)
        self.ekran_liderlik.setLayout(ana_layout)
        self.stacked_widget.setCurrentIndex(4)

    # ----------------------------------------------------
    # EKRAN 6: ETKİNLİKLER VE NOKTALAR EKRANI
    # ----------------------------------------------------
    # ----------------------------------------------------
    # EKRAN 6: ETKİNLİKLER VE NOKTALAR EKRANI (SÜTUNLAR DÜZELTİLDİ)
    # ----------------------------------------------------
    def tasarla_etkinlikler(self):
        # Sütun genişlik yönetimi için gerekli PyQt5 sınıfını lokal olarak çağırıyoruz
        from PyQt5.QtWidgets import QHeaderView

        if self.ekran_etkinlikler.layout():
            QWidget().setLayout(self.ekran_etkinlikler.layout())

        ana_layout = QHBoxLayout()
        ana_layout.setContentsMargins(0, 0, 0, 0)
        ana_layout.addWidget(self.sol_menu_olustur())

        sag_icerik = QWidget()
        sag_layout = QVBoxLayout(sag_icerik)
        sag_layout.setContentsMargins(30, 30, 30, 30)

        # --- 1. TABLO: ETKİNLİKLER ---
        lbl_etk = QLabel("📅 Yaklaşan Çevre Etkinlikleri")
        lbl_etk.setFont(QFont("Segoe UI", 12, QFont.Bold))
        sag_layout.addWidget(lbl_etk)
        
        tablo_etk = QTableWidget()
        tablo_etk.setColumnCount(3)
        tablo_etk.setHorizontalHeaderLabels(["Etkinlik Adı", "Yer / Kampüs", "Tarih"])
        tablo_etk.setAlternatingRowColors(True)
        
        # Sütun genişliklerini otomatik ve esnek yapma kuralları:
        tablo_etk.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive) # Elle büyütülebilme
        tablo_etk.horizontalHeader().setStretchLastSection(True) # Son sütunu sona yasla
        
        etkinlikler = db.get_events()
        tablo_etk.setRowCount(len(etkinlikler))
        for r_idx, row in enumerate(etkinlikler):
            tablo_etk.setItem(r_idx, 0, QTableWidgetItem(str(row[0])))
            tablo_etk.setItem(r_idx, 1, QTableWidgetItem(str(row[1])))
            tablo_etk.setItem(r_idx, 2, QTableWidgetItem(str(row[2])))
        
        # VERİLER YAZILDIKTAN SONRA GENİŞLİKLERİ İÇERİĞE GÖRE HESAPLA (KRİTİK ADIM)
        tablo_etk.resizeColumnsToContents()
        # Sütunların ilk ikisini içeriğe göre esnet, tarih sütununu sabit tut veya yay:
        tablo_etk.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        tablo_etk.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        sag_layout.addWidget(tablo_etk)

        # --- 2. TABLO: GERİ DÖNÜŞÜM NOKTALARI ---
        lbl_nokta = QLabel("📍 En Yakın Geri Dönüşüm Noktaları")
        lbl_nokta.setFont(QFont("Segoe UI", 12, QFont.Bold))
        sag_layout.addWidget(lbl_nokta)
        
        tablo_nokta = QTableWidget()
        tablo_nokta.setColumnCount(2)
        tablo_nokta.setHorizontalHeaderLabels(["Merkez Adı", "Açık Adres"])
        tablo_nokta.setAlternatingRowColors(True)
        
        noktalar = db.get_recycling_points()
        tablo_nokta.setRowCount(len(noktalar))
        for r_idx, row in enumerate(noktalar):
            tablo_nokta.setItem(r_idx, 0, QTableWidgetItem(str(row[0])))
            tablo_nokta.setItem(r_idx, 1, QTableWidgetItem(str(row[1])))
            
        # Merkezler tablosu için de aynı akıllı esnekliği uyguluyoruz:
        tablo_nokta.resizeColumnsToContents()
        tablo_nokta.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        tablo_nokta.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        sag_layout.addWidget(tablo_nokta)

        ana_layout.addWidget(sag_icerik)
        self.ekran_etkinlikler.setLayout(ana_layout)
        self.stacked_widget.setCurrentIndex(5)

    # ----------------------------------------------------
    # EKRAN 7: YÖNETİCİ (ADMIN) PANELİ (GÜNCELLENDİ)
    # ----------------------------------------------------
    # ----------------------------------------------------
    # EKRAN 7: YÖNETİCİ (ADMIN) PANELİ - EN GÜVENLİ SÜRÜM
    # ----------------------------------------------------
    def tasarla_admin(self):
        if self.ekran_admin.layout():
            QWidget().setLayout(self.ekran_admin.layout())

        ana_layout = QHBoxLayout()
        ana_layout.setContentsMargins(0, 0, 0, 0)

        # Sol Kontrol Paneli Şeridi
        sol_panel = QFrame()
        sol_panel.setFixedWidth(200)
        sol_panel.setStyleSheet("background-color: #0F172A;")
        sol_lay = QVBoxLayout(sol_panel)
        
        lbl_title = QLabel("Yönetici Paneli")
        lbl_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl_title.setStyleSheet("color: #EF4444; margin-bottom: 20px;")
        sol_lay.addWidget(lbl_title, alignment=Qt.AlignCenter)
        
        btn_cikis = QPushButton("Sistemden Çık")
        btn_cikis.setStyleSheet("background-color: #EF4444; color: white; border-radius:6px; min-height: 35px; font-weight: bold;")
        btn_cikis.clicked.connect(self.islem_cikis)
        sol_lay.addStretch()
        sol_lay.addWidget(btn_cikis)
        ana_layout.addWidget(sol_panel)

        sag_icerik = QWidget()
        sag_ana_layout = QHBoxLayout(sag_icerik)

        # Sol Blok: Veri Giriş Formları
        sol_blok = QWidget()
        sol_blok_lay = QVBoxLayout(sol_blok)

        # 1. ETKİNLİK EKLEME FORMU
        sol_blok_lay.addWidget(QLabel("📅 Yeni Etkinlik Tanımla"))
        f1_frame = QFrame()
        f1_frame.setStyleSheet("background-color: white; padding: 15px; border-radius: 8px; border:1px solid #E2E8F0;")
        f1_v_lay = QVBoxLayout(f1_frame)
        
        f1_lay = QFormLayout()
        self.txt_adm_etk_baslik = QLineEdit()
        self.txt_adm_etk_yer = QLineEdit()
        self.txt_adm_etk_tarih = QLineEdit(); self.txt_adm_etk_tarih.setPlaceholderText("YYYY-MM-DD")
        f1_lay.addRow("Etkinlik Adı:", self.txt_adm_etk_baslik)
        f1_lay.addRow("Mekan:", self.txt_adm_etk_yer)
        f1_lay.addRow("Tarih:", self.txt_adm_etk_tarih)
        f1_v_lay.addLayout(f1_lay)
        
        btn_etk_ekle = ModernButton("Etkinliği Yayınla")
        btn_etk_ekle.clicked.connect(self.islem_admin_etkinlik_ekle)
        f1_v_lay.addWidget(btn_etk_ekle)
        
        sol_blok_lay.addWidget(f1_frame)

        # 2. MERKEZ/NOKTA EKLEME FORMU
        sol_blok_lay.addWidget(QLabel("📍 Yeni Geri Dönüşüm Noktası Ekle"))
        f2_frame = QFrame()
        f2_frame.setStyleSheet("background-color: white; padding: 15px; border-radius: 8px; border:1px solid #E2E8F0;")
        f2_v_lay = QVBoxLayout(f2_frame)
        
        f2_lay = QFormLayout()
        self.txt_adm_nokta_adi = QLineEdit()
        self.txt_adm_nokta_adres = QLineEdit()
        f2_lay.addRow("Nokta Adı:", self.txt_adm_nokta_adi)
        f2_lay.addRow("Adres:", self.txt_adm_nokta_adres)
        f2_v_lay.addLayout(f2_lay)
        
        btn_nokta_ekle = ModernButton("Noktayı Sisteme Ekle")
        btn_nokta_ekle.clicked.connect(self.islem_admin_nokta_ekle)
        f2_v_lay.addWidget(btn_nokta_ekle)
        
        sol_blok_lay.addWidget(f2_frame)
        sol_blok_lay.addStretch()
        
        sag_ana_layout.addWidget(sol_blok, stretch=1)

        # Sağ Blok: Canlı Kullanıcı Listesi
        sag_blok = QWidget()
        sag_blok_lay = QVBoxLayout(sag_blok)
        sag_blok_lay.addWidget(QLabel("👥 Kayıtlı Kullanıcı Listesi & Yönetimi"))

        self.tablo_kullanicilar = QTableWidget()
        self.tablo_kullanicilar.setColumnCount(5)
        self.tablo_kullanicilar.setHorizontalHeaderLabels(["ID", "Ad Soyad", "Kullanıcı Adı", "Fidan S.", "İşlem"])
        self.tablo_kullanicilar.setAlternatingRowColors(True)
        self.tablo_kullanicilar.horizontalHeader().setStretchLastSection(True)
        
        self.admin_kullanici_listesini_yenile()
        
        sag_blok_lay.addWidget(self.tablo_kullanicilar)
        sag_ana_layout.addWidget(sag_blok, stretch=2)

        ana_layout.addWidget(sag_icerik)
        self.ekran_admin.setLayout(ana_layout)

    def admin_kullanici_listesini_yenile(self):
        """Admin panelindeki kullanıcı tablosunu günceller ve silme butonlarını bağlar."""
        kullanicilar = db.get_all_users()
        self.tablo_kullanicilar.setRowCount(len(kullanicilar))
        
        for idx, user in enumerate(kullanicilar):
            self.tablo_kullanicilar.setItem(idx, 0, QTableWidgetItem(str(user[0])))
            self.tablo_kullanicilar.setItem(idx, 1, QTableWidgetItem(str(user[1])))
            self.tablo_kullanicilar.setItem(idx, 2, QTableWidgetItem(str(user[2])))
            self.tablo_kullanicilar.setItem(idx, 3, QTableWidgetItem(f"{user[5]} Fidan"))
            
            # Dinamik Silme Butonu Oluşturma
            btn_sil = QPushButton("Sil")
            btn_sil.setStyleSheet("background-color: #CH3C3C; background: #E74C3C; color: white; font-weight: bold; max-width: 60px;")
            # Satır numarasını ve kullanıcı ID'sini butona bağlıyoruz
            btn_sil.clicked.connect(lambda checked, u_id=user[0]: self.islem_admin_kullanici_sil(u_id))
            self.tablo_kullanicilar.setCellWidget(idx, 4, btn_sil)

    def islem_admin_kullanici_sil(self, user_id):
        emin_mi = QMessageBox.question(self, "Kullanıcı Sil", "Bu kullanıcıyı ve tüm atık geçmişini silmek istediğinize emin misiniz?", 
                                       QMessageBox.Yes | QMessageBox.No)
        if emin_mi == QMessageBox.Yes:
            db.delete_user_by_admin(user_id)
            QMessageBox.information(self, "Başarılı", "Kullanıcı sistemden tamamen kaldırıldı.")
            self.admin_kullanici_listesini_yenile() # Tabloyu hemen güncelle

    def islem_admin_etkinlik_ekle(self):
        baslik = self.txt_adm_etk_baslik.text()
        yer = self.txt_adm_etk_yer.text()
        tarih = self.txt_adm_etk_tarih.text()
        if baslik and yer and tarih:
            db.add_event_by_admin(baslik, yer, tarih)
            QMessageBox.information(self, "Başarılı", "Yeni etkinlik başarıyla eklendi!")
            self.txt_adm_etk_baslik.clear()
            self.txt_adm_etk_yer.clear()
            self.txt_adm_etk_tarih.clear()
        else:
            QMessageBox.warning(self, "Hata", "Lütfen tüm admin alanlarını doldurun!")

    def islem_admin_nokta_ekle(self):
        isim = self.txt_adm_nokta_adi.text()
        adres = self.txt_adm_nokta_adres.text()
        if isim and adres:
            db.add_point_by_admin(isim, adres)
            QMessageBox.information(self, "Başarılı", "Geri dönüşüm noktası sisteme eklendi!")
            self.txt_adm_nokta_adi.clear()
            self.txt_adm_nokta_adres.clear()
        else:
            QMessageBox.warning(self, "Hata", "Lütfen tüm admin alanlarını doldurun!")


# ==========================================
# UYGULAMANIN ÇALIŞTIRILMA DÖNGÜSÜ
# ==========================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = YesilIzApp()
    pencere.show()
    sys.exit(app.exec_())