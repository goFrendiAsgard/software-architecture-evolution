# Tentang Repository Ini

Repository ini adalah penjabaran dari artikel [Evolusi Perangkat Lunak](https://www.notion.so/gofrendi/Evolusi-Arsitektur-Perangkat-Lunak-1e80ad470b734ad4ab22d04e25ea372e).

Studi kasus yang akan dipakai di sini adalah voting pokemon. Pengguna akan dapat memilih/menambahkan pokemon favorit mereka sekaligus melihat hasil voting secara keseluruhan.

Pembuatan aplikasi akan diawali mulai dari arsitektur paling sederhana, hingga pada akhirnya mengarah pada microservices.

Karena kita akan menjalankan beberapa aplikasi/tasks dalam urutan tertentu, maka di sini kita akan menggunakan [zaruba](https://github.com/state-alchemists/zaruba), sebuah declarative task runner yang bisa memenuhi kebutuhan tersebut.

Selain `zaruba`, kita juga akan menggunakan [pipenv](https://pipenv.pypa.io/en/latest/) untuk me manage python environment di setiap aplikasi.

Beberapa aplikasi third party seperty `rabbitmq` dan `mysql` juga akan dijalankan menggunakan docker.

> __TIPS:__ Jika kalian menggunakan ubuntu dan sudah menginstall zaruba, kalian bisa menjalankan perintah berikut untuk menginstall dependency lainnya:

```bash
zaruba please setupContoh -i
```

# Konfigurasi Ports

Beberapa aplikasi yang akan kita jalankan akan bisa diakses melalui port-port tertentu di komputer lokal kita. Secara default port-port yang akan dipakai adalah sebagai berikut:

```yaml
dbExample:
    mySQL       : 3306
messageBusExample:
    rabbitmq    : 5672
    web         : 15672
frontendMonolith: 
    web         : 3000
backendMonolith:
    web         : 3010
frontendMicroservice:
    web         : 5000
backendGateway:
    web         : 5010
backendFetcher:
    web         : 5020 (tidak melayani API request)
backendFetcher2:
    web         : 5021 (tidak melayani API request)
backendFetcher3:
    web         : 5022 (tidak melayani API request)
backendVoter:
    web         : 5030 (tidak melayani API request)
dbWarehouseExample:
    mySQL       : 3307
dataStreamer:
    web         : 7000 (tidak melayani API request)
jupyter:
    web         : 8000
```

Kita bisa mengubah port-port yang ada melalui konfigurasi environment variable. Caranya dengan mengcopy `template.env` ke `.env` dan melakukan modifikasi seperlunya.

# Arsitektur 1: Input, Process, Output

Ini adalah arsitektur paling sederhana yang bisa buat. Arsitektur ini hanya terdiri dari sekitar 40 baris kode python. Detailnya bisa dilihat di [simple/main.py](simple/main.py). 

![skema](images/arsitektur-01-skema.png)

Pada dasarnya, kita akan menyimpan data voting pada variable `pokemon_vote_result` yang bertipe `dictionary`.

Selanjutnya, secara terus menerus, program akan meminta inputan user berupa angka antara 1 sampai 3.

Jika user memasukkan angka 1, maka program akan menampilkan isi variable `pokemon_vote_result`.

Jika user memasukkan angka 2, maka program akan menanyakan nama pokemon yang hendak dipilih. Nama pokemon tersebut kemudian akan digunakan untuk mengubah nilai variable `pokemon_vote_result`.

Selanjutnya jika user memasukkan angka 3, maka program akan berakhir.

Untuk menjalankan program, kita bisa menggunakan perintah berikut:

```bash
cd simple
python main.py
```

![Tampilan program](images/arsitektur-01-tampilan.png)

## Pros

* Arsitektur stand alone seperti ini tergolong sederhana dan mudah di maintain.
* Hampir tidak ada dependency ke aplikasi third parties

## Cons

* Data tersimpan di RAM, sehingga akan hilang jika program dimatikan

# Arsitektur 2: Input, Process, Output, dan Storage

Untuk menyimpan data secara permanen, kita membutuhkan akses ke harddisk baik secara langsung maupun melalui aplikasi third party seperti DBMS.

Di sini, kita akan menggunakan salah satu DBMS yang sudah cukup terkenal yakni MySQL.

Alih-alih mengakses file secara langsung, MySQL menyediakan interface SQL (Structured Query Language). Mempelajari SQL adalah suatu keniscayaan lantaran banyak DBMS yang menggunakan bahasa ini.

> __CATATAN:__ Untuk data yang terbatas (misal konfigurasi game), menyimpan data dalam bentuk file mungkin adalah pilihan yang lebih baik.

Beberapa fakta menarik tentang SQL:

* Beberapa DBMS "no-SQL" pun menyediakan interface yang mirip dengan SQL. Cassandra memiliki CQL, Cockroach DB juga memiliki syntax serupa.
* Kita bisa mengakses data dari google sheet menggunakan SQL jika kita menggunakan query engine semacam [presto/trino](https://trino.io/docs/current/connector/googlesheets.html).

Saat kita menggunakan SQL, maka paradigma kita terhadap data harus sedikit disesuaikan. Data-data yang kita miliki harus dibentuk dalam struktur tabel-tabel dengan banyak kolom.

Karena itu, kali ini kita tidak lagi menggunakan struktur dictionary.

> __CATATAN:__ Ada beberapa DBMS no-SQL yang mendukung penyimpanan dalam bentuk key-value (mirip dictionary). Misalnya redis.

Detail program kali ini bisa dilihat di [simple/main.py](simple-db/main.py).

![skema](images/arsitektur-02-skema.png)

Jika diperhatikan dengan seksama, di sini ada beberapa perbedaan dibandingkan program sebelumnya:

* Butuh library external seperti SQLAlchemy
* Karena data disimpan dalam bentuk tabel, maka perlu langkah tambahan untuk menampilkan ulang (perhatikan fungsi `get_vote_result`)
* Program perlu tahu bagaimana cara menghubungi database melalui variable `connection_string`.
* Selain bisa menggunakan SQL, SQLAlchemy juga mengijinkan kita menggunakan ORM (Object relational mapping). Artinya tabel kita akan dipetakan ke dalam sebuah class dan setiap baris di dalam tabel bisa diperlakukan seperti instance dari class tersebut (perhatikan class `PokemonVote` dan fungsi `vote_pokemon`)

> __CATATAN:__ Sqlite adalah salah satu DBMS paling sederhana. Cocok untuk menyimpan data terstruktur dalam jumlah kecil. Secara default, program yang kita buat akan menggunakan sqlite dengan penyimpanan di RAM seandainya environment variable `CONNECTION_STRING` tidak ditemukan.

Untuk menjalankan program kita kali ini, diperlukan langkah-langkah yang agak panjang:

```bash
# membuat/menjalankan docker container dbExample (MySQL)
zaruba please runDbExample

# setelah dbExample ready, kita bisa menekan ctrl + c atau membuka terminal baru
# docker akan tetap berjalan di balik layar.
# selain menggunakan zaruba, kita juga bisa menggunakan perintah `docker run`

# menginstall dependency program
cd simple-db
pipenv install

# Setup environment variable
export CONNECTION_STRING=mysql+pymysql://root:toor@localhost:3306/sample

# bisa juga menggunakan `source mysql.env`.
# berguna jika memiliki banyak environment variable yang perlu diisi.


# menjalankan program
pipenv run python ./main.py
```

Tampilan program akan persis sama seperti sebelumnya, tapi sekarang data yang kita masukkan akan tersimpan secara permanen.

> __TIPS:__ Perintah di atas bisa disimpan dalam bentuk shell script untuk dijalankan di kesempatan berikutnya. Cara yang lain, bisa juga menggunakan perintah ini:

```bash
zaruba please runSimpleDb -i
```

## Pros

* Data tersimpan secara permanen
* Beberapa aplikasi bisa berbagi data yang sama

## Cons

* Koneksi ke DBMS harus dipastikan lancar
* DBMS bisa menjadi bottleneck dan single point of failure.
* Dalam banyak kasus membutuhkan transformasi data untuk menyesuaikan dengan format yang didukung oleh DBMS
* Jika DBMS bisa diakses dari luar, maka keamanan data akan bermasalah. Siapapun mungkin melakukan akses langsung melalui interface SQL.

# Arsitektur 3: Client/Server, Frontend dan Backend

Pada arsitektur sebelumnya, kita bisa memandang DBMS sebagai server, dan aplikasi-aplikasi yang mengakses database sebagai client. Arsitektur tersebut tampaknya pernah populer dan barangkali pula masih banyak dipakai untuk kepentingan internal.

Adapun demikian, kelemahan terbesar dari arsitektur sebelumnya adalah DBMS bisa diakses siapa saja yang memiliki credential baik secara sah maupun tidak. Ini bisa berakibat fatal, karena seseorang bisa mem-bypass validasi yang telah dibuat di sisi program.

Sebagai contoh, seorang hacker yang iseng bisa mengupdate harga jual menjadi angka negatif dengan kalimat SQL seperti ini:

```sql
UPDATE barang SET harga=-50000;
```

Untuk mengatasi hal ini, kita perlu membuat server-side program yang melakukan segala validasi dan menjamin integritas data.

Walau tak sepenuhnya bisa mengamankan sistem, tapi pembagian aplikasi menjadi server-side dan client-side akan sangat membantu. Setidaknya sekarang aplikasi client tidak bisa melakukan hal-hal yang tidak diijinkan oleh aplikasi server.

Keberadaan teknologi web dan antar muka yang semakin canggih membuat arsitektur ini menjadi kian populer dan berkembang pesat.

Aplikasi client side sendiri sebenarnya bisa dibagi menjadi dua macam:

* Aplikasi client yang membutuhkan instalasi khusus seperti mobile app atau aplikasi game online.
* Aplikasi client yang tidak membutuhkan instalasi khusus seperti script HTML/CSS/JavaScript yang didownload dari server dan dijalankan di client.

Kali ini, kita akan mencoba untuk membuat client side jenis kedua dengan framework `svelte`.

Sebelum melangkah lebih jauh, kira-kira beginilah skema aplikasi kita:

![Skema](images/arsitektur-03-skema.png)

Kode aplikasi frontend terletak di [folder frontend](frontend), sedangkan kode aplikasi backend terletak di [folder backend-monolith](backend-monolith).

Untuk menjalankan kedua aplikasi tersebut, lengkap dengan databasenya, kita bisa menggunakan perintah berikut:

```bash
zaruba please runMonolith
```

Tampilan aplikasi adalah sebagai berikut:

![Tampilan](images/arsitektur-03-tampilan.png)

Kita bisa melihat bahwa setiap kali kita menekan tombol `vote`, maka aplikasi backend akan menerima request `POST` dari frontend dan memberikan balasan.

Demikian pula secara periodik dan saat frontend pertama kali dijalankan, maka aplikasi frontend akan mengirimkan request `GET` sehingga aplikasi backend dapat melakukan query ke database dan memberikan balasan berupa akumulasi voting saat ini.

## Pros

* Integritas data lebih terjaga karena divalidasi oleh backend
* Beberapa aplikasi frontend dapat mengakses backend yang sama

## Cons

* Aplikasi backend harus dipastikan selalu berjalan
* Lebih sulit di manage daripada arsitektur sebelumnya
* Perubahan frontend dan backend harus sejalan. Biasanya backend perlu memiliki API versioning untuk meng-handle perubahan struktur data. Terutama jika frontend dan backend di-deploy dalam waktu yang berbeda.

> __CATATAN:__ Beberapa framework seperti Laravel/Django menganut konsep MVC/MVT di mana frontend dan backend terletak dalam code base yang sama. Proses rendering frontend pun sebagian dilakukan di server. Framework-framework tersebut sangat disarankan jika kita tidak memiliki tim frontend yang dedicated.

# Arsitektur 4: Microservices

Dalam banyak kasus, arsitektur client-server dengan backend monolith sudah cukup untuk menangani kebutuhan bisnis.

Namun tak bisa dipungkiri, terkadang ada bagian-bagian backend yang:
* lebih baik ditulis dalam bahasa pemrograman berbeda
* perlu di scale secara berbeda
* dikembangkan oleh tim yang berbeda

Pemanggilan fungsi yang semula bisa dilakukan secara internal dalam satu aplikasipun kini perlu dilakukan melalui jaringan.

## Komunikasi Antar Service

Secara umum, komunikasi antar service dalam microservices bisa dibedakan berdasarkan:
* Keberadaan service yang me-manage service-service lain (Orchestration vs Choreography)
* Apakah pengirim pesan perlu memunggu balasan atau tidak perlu (Synchronous vs Asynchronous, Command vs Query)

Mari kita coba dalami beberapa istilah di atas:
* __Orchestration__: Ada satu service yang berfungsi sebagai orchestrator untuk menentukan urutan permintaan request (misalnya setelah mendapat balasan dari service A, si orchestrator perlu mengirim request ke service B berdasarkan balasan dari A)
* __Choreography__: Tidak ada service yang bergungsi serbagai orchestrator. Masing-masing service bekerja secara mandiri. Biasanya dengan cara mendengarkan event/kejadian tertentu dan mengirimkan event/kejadian lain (misalnya, setiap kali service A mendengar event tertentu, service A akan melakukan proses dan mengirimkan beberapa event lain. Service-service yang lain hanya perlu mendengar event yang sesuai dengan domain mereka)
* __Synchronous__: Artinya proses pada sebuah service perlu menunggu balasan dari service lain sebelum bisa dilanjutkan.
* __Asynchronous__: Artinya proses pada sebuah service bisa terus beerlanjut, terlepas ada tidaknya balasan dari service lain.
* __Command__: Perintah yang mengubah state sistem.
* __Query__: Permintaan data yang membutuhkan balasan tanpa adanya perubahan state.

Dalam prakteknya, terminologi dan penggolongan komunikasi ini kerap kali tumpang tindih. Belum lagi, dalam banyak kasus kita perlu menggunakan beberapa pola komunikasi untuk menyesuaikan dengan use case yang kita miliki.

Biasanya komunikasi pada pola choreography cenderung asynchronous, sedangkan pada pola orchestration cenderung synchronous (tapi tidak selalu demikian). Biasanya pula, command bisa dikerjakan secara asynchronous sedangkan query dikerjakan secara synchronous.

Perbandingan pola komunikasi synchronous vs asynchronous kurang lebih begini:

```
SYNCHRONOUS

Service A                  Service B
========================   ================================
mengirim request ke B      ...
menunggu                   menerima request dari A
menunggu                   melakukan proses
menunggu                   memberikan response balasan ke A
menerima response dari B   ...
melanjutkan proses         ...

ASYNCHRONOUS

Service A                                          Service B
================================================   =======================
menunggu balasan dari B    ...                     ...
...                        mengirim request ke B   ...
...                        melanjutkan proses      menerima request dari A
...                        melanjutkan proses      melakukan proses
...                        melanjutkan proses      mengirim balasan ke A
menerima response dari B   ...                     ...
memproses balasan          ...                     ...
```

>__CATATAN:__ Dalam kenyataannya pola asynchronous juga membutuhkan pemrosesan parallel atau concurrent dari sisi program. Node JS mendukung ini melalui mekanisme `Promise`, sementara Golang mendukung ini dengan `channel` dan `go routine`. Untuk bahasa-bahasa seperti C/Pascal, kita bisa menggunakan `multi-threading`.

Pola komunikasi asynchronous kerap melibatkan keberadaan message broker/message bus. Keberadaan message broker/message bus memungkinkan tiap service tidak perlu saling mengetahui posisi service lain.

Di satu sisi keberadaan message broker/message bus ini memudahkan kita untuk me manage service-service yang begitu banyak. Namun di sisi lain, ini bisa menjadi single point of failure juga.

## Pakai Pola Komunikasi yang Mana?

### Asynchronous

![](images/radio.jpg)

Pola komunikasi asynchronous umumnya digunakan jika kita ingin melakukan perubahan state pada sistem dan tidak membutuhkan balasan seketika. Pola komunikasi ini membutuhkan message bus sebagai jembatan komunikasi antar service.

Keberadaan message bus di sini membuat setiap service tidak perlu saling mengenal satu sama lain (loosly coupled). Namun demikian, message bus juga memperkenalkan beberapa masalah baru, antara lain:

* Message bus menjadi single point of failure. Jika message bus sampai mati, maka semua proses komunikasi akan terhenti.
* Proses tracing data bisa jadi lebih susah. Kita kadang tidak yakin service mana saja  yang membuat/menghandle sebuah event.

Beberapa message bus yang sering dipakai antara lain:

* Nats
* Kafka
* RabbitMq


### Synchronous

![](images/phone.jpg)

Secara umum, jika kita ingin melakukan query yang membutuhkan balasan tanpa ada perubahan state, maka pola komunikasi synchronous lebih digemari. Pola komunikasi synchronous bisa diterapkan dengan beberapa cara:

* HTTP request/response
* GRPC
* RPC pada message bus

Penggunaan message bus untuk komunikasi synchronous kadang terkesan tidak intuitif, karena message bus biasanya digunakan untuk pola komunikasi asynchronous. Namun demikian, message bus juga bisa berfungsi sebagai buffer antrian, sehingga pesan-pesan yang masuk tidak diproses secara seketika.

RPC pada message bus umumnya memanfaatkan dua event.:
* Event pertama adalah event balasan. Si pengirim pesan harus terlebih dahulu mendengarkan pesan dari event balasan sebelum mengirimkan pesannya. Nama event balasan biasanya juga ikut disertakan bersama dengan pesan yang hendak dikirim.
* Event kedua adalah event utama. Si penerima pesan akan mendengarkan pesan dari event ini, lengkap dengan nama event balasan yang diharapkan. Selanjutnya, pesan balasan akan dikirimkan ke event balasan untuk diterima oleh pengirim pesan.

## Pokemon Vote

Kembali ke kasus voting pokemon kita tadi. Semisal setelah aplikasi tersebut kita launch, kita tahu bahwa request untuk melihat hasil voting ternyata jauh lebih banyak daripada requst untuk melakukan voting itu sendiri.

Di sinilah salah satu kelebihan microservice. Kita bisa melakukan scaling setiap service secara berbeda.

Sebelum masuk lebih jauh, mari kita awali dengan sebuah skema:

![Skema](images/arsitektur-04-skema.png)

Dibandingkan dengan skema di arsitektur sebelumnya, sekarang kita bisa melihat bahwa aplikasi backend di sini kita pecah menjadi tiga aplikasi terpisah:

* Backend-gateway: Bertangung jawab menangani request dari frontend dan mengirimkan message ke message bus (RabbitMq)
* Backend-fetcher: Bertanggung jawab untuk mendapatkan data vote dan setiap kali ada permintaan melalui message bus dan memberikan balasan ke event/topic yang telah ditentukan.
* Backend-voter: Bertanggung jawab untuk melakukan operasi insert ke dalam database

>__CATATAN:__ Dalam banyak kasus, service-service pada arsitektur microservices memiliki database yang berbeda-beda pula. Selain itu, untuk membaca data umumnya digunakan caching mechanism (misalnya menggunakan redis). Pada contoh ini kita melakukan penyederhanaan supaya arsitekturnya tidak semakin rumit :p

### Backend Fetcher

Karena aplikasi backend sudah kita pecah menjadi beberapa service, maka kita bisa menerapkan aturan scaling yang berbeda pada masing-masing aplikasi. Misalnya, kita bisa membuat tiga buah service `backend-fetcher` yang masing-masing mendengarkan pesan dari event yang sama.

![3 fetcher](images/arsitektur-04-data-fetcher.png)

Perhatikan pada bagian yang diberi lingkaran biru. Terlihat jelas bahwa tiga buah request yang sampai ke `backend-gateway` ternyata di belakangnya diproses oleh `backend-fetcher` yang berbeda-beda.

Ini mirip dengan keberadaan beberapa kasir di bank/pasar swalayan. Semakin banyak service yang bekerja, maka antrian message pun akan semakin cepat habis. Response ke user pun akan terlihat lebih cepat.

Komunikasi antara backend gateway dan backend fetcher secara detail adalah sebagai berikut:

```
Backend Gateway                                       Backend Fetcher
===================================================   ========================
Menerima HTTP request      ...                        ...
...                        Menunggu balasan fetcher   ...
Mengirim RPC ke fetcher    ...                        ...
...                        ...                        Menerima RPC request
...                        ...                        Mendapatkan data dari DB
...                        ...                        Mengirim balasan
...                        Menerima balasan           ...
Mengirim HTTP response     ...                        ...
```

### Backend Voter

Kita bisa melihat bahwa saat user ingin menampilkan total vote, maka kita mutlak memerlukan balasan dari server.

Kenyataannya, tidak semua proses komunikasi membutuhkan balasan seketika. Misalnya saat kita melakukan vote, maka yang penting datanya sampai ke server. Untuk masalah visualisasi, kita bisa melakukan penambahan secara mandiri di sisi client. Ini biasanya cocok untuk kasus yang membutuhkan proses sangat lama (training ML Model misalnya). Balasan ke user bisa dikirim melalui channel yang berbeda (misalnya melalui email). Yang jelas kita hanya perlu tahu bahwa request kita sudah diterima oleh server.

Jika kita mengamati log pada `backend-fetcher`, maka kita bisa melihat bahwa request yang dikirim oleh `backend-gateway` tidak pernah dibalas kembali.

![voter](images/arsitektur-04-data-voter.png)

Komunikasi dengan backend voter secara detail adalah sebagai berikut

```
Backend Gateway           Backend Voter                   Data Streamer
=======================   =============================   ================================
Menerima HTTP request     ...                             ...
Mengirim event new_vote   ...                             ...
Mengirim HTTP response    Menerima event new_vote         ...
...                       Menyimpan vote ke DB            ...
...                       Mengirim event new_vote_saved   ...
...                       ...                             Menerima event ke new_vote_saved
...                       ...                             Menyimpan ke DB warehouse
```

## Praktek

Untuk menjalankan aplikasi yang sudah dipecah-pecah menjadi micro-services ini, kita bisa menjalankan

```bash
zaruba please runMicroServices
```

Kalian juga bisa mencoba menjalankan semua microservices kecuali `backend-voter` dengan cara berikut:

```bash
zaruba please runFrontendMicroservices runBackendGateway runBackendFetcher
```

Semua akan tampak normal, hanya saja kita tidak bisa melakukan vote.

## Pros

* Jika salah satu service mati, keseluruhan sistem masih bisa berjalan
* Bisa melakukan scaling secara berbeda
* Bisa dikembangkan oleh tim yang berbeda dengan bahasa pemrograman/teknologi yang berbeda.

## Cons

* Susah di manage
* Kompleksitasnya tinggi
* Adanya network latency untuk komunikasi antar service
* Debugnya sulit

>__CATATAN:__ Di dunia nyata, untuk me-manage microservices, kita kerap menggunakan orchestrator semacam kubernetes. Setiap service juga perlu di-package menjadi container sebelum di deploy.


# Bonus: Data + ML

Data dan ML sebenarnya merupakan bagian yang terpisah dari arsitektur perangkat lunak. Namun di sini mari kita sedikit membahas tentang letak dan peranan kedua benda tersebut.

Secara bisnis, data dan ML bisa menunjang kita dalam mengambil keputusan taktis strategis. Umumnya data yang kita kumpulkan berguna untuk mengevaluasi kinerja produk/layanan kita, sedangkan ML bisa digunakan untuk melakukan prediksi.

Jika diperhatikan, pada arsitektur sebelumnya, ada beberapa komponen yang belum dibahas:

* Data streamer
* Data warehouse
* Jupyter

Data streamer akan membaca event `new_vote_saved`, melakukan transformasi dengan menambahkan kolom `day_bucket` dan menyimpannya ke data warehouse. Proses ini kerap kali disebut pula dengan ETL (Extract-Transform-Load)

>__CATATAN:__ Untuk kepentingan yang lebih serius, biasanya digunakan spark dan airflow.

Hasil transformasi data tersebut adalah sebagai berikut:

![db vs warehouse](images/data-db-vs-warehouse.png)

Selanjutnya, proses analisa data dan pelatihan model machine learning akan menggunakan data warehouse ini alih-alih mengunakan database operasional.

Sebelum melanjutkan pembahasan, kita perlu tahu bahwa data baru akan berguna jika jumlahnya sudah cukup banyak. Membuat pipeline data barangkali adalah investasi jangka panjang yang tidak seketika menghasilkan profit, tapi memakan biaya operasional.

Mari kita mulai dengan men-generate data voting selama 4 bulan ke belakang.

```bash
zaruba please seedData
```

Setelah selesai menjalankan perintah tersebut, seharusnya data warehouse kita akan terisi dengan banyak data

![data-generated](images/data-generated.png)

Dengan keberadaan data warehouse ini, kita bisa melakukan dua hal:
* Menampilkan data-data masa lalu dalam bentuk yang bermakna
* Memprediksi masa depan

## Masa Lalu

Mari kita mulai dengan menampilkan data masa lalu.

```bash
zaruba please runJupyter
```

Hasilnya kurang lebih sebagai berikut:

![masa lalu](images/data-masa-lalu.png)

Di sini kita bisa melihat adanya tren voting untuk beberapa pokemon

## Masa depan

Dari data yang ada kita, kita bisa melakukan beberapa processing supaya bisa digunakan untuk training ML model.

Secara sederhana, untuk memprediksi data vote besok, kita bisa menggunakan data vote 4 hari ke belakang (atau sesuai hasil eksperimen). Selanjutnya dengan mengunakan data prediksi vote besok dan data vote 3 hari ke belakang, kita bisa memprediksi jumlah vote untuk besok lusa. Demikian seterusnya. 

![masa depan](images/data-masa-depan.png)

>__CATATAN:__ Dalam prakteknya, model machine learning masih perlu di fine-tuning, dan kerap melibatkan banyak eksperimen. Tapi untuk kesempatan kali ini, mari kita akhiri di sini. :)

Terima kasih sudah mengikuti sejauh ini. Sampai jumpa di artikel/kesempatan berikutnya :)