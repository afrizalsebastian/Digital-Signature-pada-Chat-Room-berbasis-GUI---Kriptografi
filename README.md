# Digital-Signature-pada-Chat-Room-berbasis-GUI
# IF4020 - Kriptografi
## Garis Besar
Program dibuat dengan bahasa python dan berbasi GUI. Library GUI yang digunakan adalah Tkinter.
Program akan membuat sebuah chatroom sederhana untuk beberapa client. Program akan mengirim pesan dari satu client ke client lainnya.
Program akan melakukan digital signature setiap pesan yang terkirim.
Program akan memeriksa digital signature pada saat pesan telah diterima oleh client dengan asumsi server bersifat aman (kesalahan yang terjadi hanya pada jaringan).
Jika terjadi perubahan pesan, maka akan diberikan peringatan.

## Cara Menjalankan
### Clone Repository
Lakukan Clone Repository terlebih dahulu
```
git clone https://github.com/afrizalsebastian/Digital-Signature-pada-Chat-Room-berbasis-GUI---Kriptografi.git
```
Lalu Buka Repository pada Root Project
<br>
### Jalankan server
Buka Terminal lalu jalankan
``` python
python server.py
```

### Jalanakn Client
Buka Terminal yang baru lalu jalankan
``` python
python client.py
```
Untuk menjalankan beberapa client, buka beberapa terminal lalu jalankan perintah diatas

### Contact
[Afrizal Sebastian - 13520120](https://github.com/afrizalsebastian)
