"""Naskah video. Satu entri = satu kalimat narasi.

say : teks yang dibacakan TTS (boleh dieja fonetik / angka ditulis huruf)
sub : teks yang tampil sebagai subtitle (default sama dengan say)
Dengan memisahkan keduanya, subtitle tetap rapi walau ejaan TTS diakali.
"""


def L(say, sub=None):
    return {"say": say, "sub": sub or say}


CHAPTERS = [
    {
        "id": "ch00", "file": "part1.py", "scene": "Ch00Hook",
        "yt": "Pembukaan",
        "lines": [
            L("Bayangkan sebuah tabung baja sepanjang seratus meter, dengan bobot ribuan ton."),
            L("Ia turun ratusan meter ke dasar laut, tempat air menekan dengan kekuatan yang sanggup meremukkan mobil seperti kaleng bekas."),
            L("Di dalamnya, puluhan manusia bernapas, makan, tidur, dan bekerja, berbulan-bulan, tanpa pernah melihat matahari."),
            L("Lalu, saat diperintahkan, raksasa itu naik ke permukaan dengan tenang, seolah-olah tidak berbobot."),
            L("Bagaimana mungkin benda sebesar itu bisa tenggelam, melayang, dan muncul kembali sesuka hati?"),
            L("Jawabannya adalah gabungan fisika yang elegan dan rekayasa luar biasa. Di video ini, kita bongkar semuanya, selapis demi selapis."),
        ],
    },
    {
        "id": "ch01", "file": "part1.py", "scene": "Ch01Prolog",
        "yt": None,
        "lines": [
            L("Sebelum kita menyelam lebih dalam, ada satu permintaan kecil."),
            L("Kalau kamu suka cara kami menjelaskan bagaimana dunia bekerja, tekan tombol subscribe, lalu aktifkan lonceng notifikasinya."),
            L("Gratis, cuma butuh satu ketukan, dan itu sangat membantu channel ini terus membuat video seperti ini."),
            L("Sudah? Bagus. Sekarang, mari kita mulai. Inilah, bagaimana kapal selam bekerja."),
        ],
    },
    {
        "id": "ch02", "file": "part1.py", "scene": "Ch02History",
        "yt": "Sejarah: mimpi menyelam",
        "lines": [
            L("Manusia sudah sangat lama bermimpi menjelajah bawah laut."),
            L("Legenda menyebut Alexander Agung pernah turun ke laut di dalam sebuah lonceng selam."),
            L("Sekitar tahun seribu enam ratus dua puluhan, penemu Belanda Cornelis Drebbel membuat kapal yang didayung di bawah permukaan Sungai Thames, di Inggris.",
              "Sekitar tahun 1620-an, penemu Belanda Cornelis Drebbel membuat kapal yang didayung di bawah permukaan Sungai Thames, di Inggris."),
            L("Lalu pada tahun seribu tujuh ratus tujuh puluh enam, di tengah Perang Kemerdekaan Amerika, kapal selam bernama Turtle dipakai dalam percobaan serangan.",
              "Lalu pada tahun 1776, di tengah Perang Kemerdekaan Amerika, kapal selam bernama Turtle dipakai dalam percobaan serangan."),
            L("Ciptaan David Bushnell ini hanya muat satu orang, dan digerakkan dengan tenaga otot."),
            L("Perang Dunia Pertama mengubah segalanya. Kapal selam Jerman, yang disebut yu-bot, terbukti menjadi senjata laut yang mematikan.",
              "Perang Dunia Pertama mengubah segalanya. Kapal selam Jerman, yang disebut U-boat, terbukti menjadi senjata laut yang mematikan."),
            L("Lompatan terbesar datang pada tahun seribu sembilan ratus lima puluh empat, saat kapal selam nuklir pertama, yu-es-es Nautilus, mulai beroperasi.",
              "Lompatan terbesar datang pada tahun 1954, saat kapal selam nuklir pertama, USS Nautilus, mulai beroperasi."),
            L("Sejak itu, kapal selam tidak lagi harus sering muncul ke permukaan. Ia bisa tinggal di bawah air selama berbulan-bulan."),
        ],
    },
    {
        "id": "ch03", "file": "part1.py", "scene": "Ch03Archimedes",
        "yt": "Fisika dasar: Hukum Archimedes",
        "lines": [
            L("Semua berawal dari satu pertanyaan sederhana. Mengapa kapal baja yang begitu berat bisa mengapung?"),
            L("Jawabannya ada pada Hukum Archimedes."),
            L("Setiap benda yang tercelup dalam air mendapat gaya dorong ke atas, yang besarnya sama dengan berat air yang dipindahkan benda itu."),
            L("Sekarang bandingkan dua gaya. Berat benda menarik ke bawah, sedangkan gaya apung mendorong ke atas."),
            L("Kalau gaya apung lebih besar, benda naik. Kalau berat lebih besar, benda tenggelam. Kalau keduanya sama persis, benda melayang di tempat."),
            L("Keadaan melayang itu disebut daya apung netral, dan itulah kondisi yang paling diinginkan oleh kapal selam."),
            L("Kuncinya adalah kepadatan. Lambung kapal selam berisi banyak ruang kosong, sehingga kepadatan rata-ratanya bisa diatur, hingga mendekati kepadatan air laut."),
            L("Dan cara mengaturnya, adalah dengan tangki ballast.", "Dan cara mengaturnya, adalah dengan tangki ballast."),
        ],
    },
    {
        "id": "ch04", "file": "part2.py", "scene": "Ch04Ballast",
        "yt": "Tangki ballast: cara menyelam dan naik",
        "lines": [
            L("Ballast adalah tangki-tangki besar yang berada di antara dua lapisan lambung kapal selam."),
            L("Ketika kapal berada di permukaan, tangki ini berisi udara, sehingga kapal ringan dan mengapung."),
            L("Untuk menyelam, awak membuka katup di bagian atas tangki."),
            L("Udara di dalam tangki keluar lewat katup itu, dan air laut masuk dari lubang di bagian bawah."),
            L("Kapal pun semakin berat, hingga akhirnya mulai tenggelam."),
            L("Begitu mendekati kedalaman yang diinginkan, awak menutup katup dan menyeimbangkan bobot kapal, sampai gaya apung dan beratnya sama."),
            L("Penyeimbangan halus dilakukan oleh tangki trim, tangki yang lebih kecil, yang memindahkan air untuk mengatur kemiringan dan bobot."),
            L("Untuk naik, prosesnya dibalik. Udara bertekanan tinggi yang tersimpan dalam tabung, disemburkan ke dalam tangki ballast."),
            L("Udara mendorong air keluar, kapal kembali ringan, dan gaya apung membawanya naik ke permukaan."),
            L("Terdengar sederhana, tapi di dalam laut, setiap kilogram harus dihitung dengan sangat teliti."),
        ],
    },
    {
        "id": "ch05", "file": "part2.py", "scene": "Ch05Planes",
        "yt": "Kemudi dan hidroplane",
        "lines": [
            L("Tangki ballast mengatur naik dan turun. Tapi bagaimana kapal selam berbelok dan mengubah arah?"),
            L("Di bagian belakang ada kemudi vertikal, yang membelokkan kapal ke kiri atau ke kanan, seperti kemudi kapal biasa."),
            L("Lalu ada hidroplane, sirip horizontal yang bekerja seperti sayap pesawat, tapi di dalam air."),
            L("Saat kapal bergerak maju, hidroplane yang dimiringkan membuat aliran air menekan sirip ke atas atau ke bawah."),
            L("Gaya itu mengarahkan hidung kapal naik atau turun, sehingga kapal bisa menukik dengan sudut tertentu."),
            L("Hidroplane hanya efektif ketika kapal bergerak. Saat diam atau sangat pelan, pengaturan kedalaman kembali mengandalkan tangki ballast dan trim."),
        ],
    },
    {
        "id": "ch06", "file": "part2.py", "scene": "Ch06Pressure",
        "yt": "Melawan tekanan laut",
        "lines": [
            L("Sekarang, tantangan terbesarnya: tekanan."),
            L("Setiap sepuluh meter turun ke dalam laut, tekanan bertambah sekitar satu atmosfer.",
              "Setiap 10 meter turun ke dalam laut, tekanan bertambah sekitar satu atmosfer."),
            L("Pada kedalaman tiga ratus meter, tekanan sudah sekitar tiga puluh kali lipat tekanan di permukaan.",
              "Pada kedalaman 300 meter, tekanan sudah sekitar 30 kali lipat tekanan di permukaan."),
            L("Artinya, setiap sentimeter persegi dinding kapal menahan beban puluhan kilogram."),
            L("Karena itu inti kapal selam, yang disebut preshur hal, atau lambung tekan, dibuat dari baja bermutu tinggi, dan pada beberapa kapal, dari titanium.",
              "Karena itu inti kapal selam, yang disebut pressure hull, atau lambung tekan, dibuat dari baja bermutu tinggi, dan pada beberapa kapal, dari titanium."),
            L("Bentuknya silinder dengan ujung melengkung. Bentuk ini membagi tekanan secara merata, sehingga tidak ada satu titik yang terlalu lemah."),
            L("Setiap kapal punya batas kedalaman uji, dan batas kedalaman hancur. Angka sebenarnya biasanya dirahasiakan oleh militer."),
            L("Itulah sebabnya setiap sambungan, katup, dan lubang di lambung dirancang dengan standar yang sangat ketat."),
        ],
    },
    {
        "id": "ch07", "file": "part3.py", "scene": "Ch07Power",
        "yt": "Tenaga penggerak: diesel, baterai, nuklir",
        "lines": [
            L("Lalu, dari mana kapal selam mendapat tenaga?"),
            L("Cara pertama adalah diesel-listrik, yang dipakai kapal selam konvensional."),
            L("Di permukaan, mesin diesel menyala dan mengisi baterai raksasa. Kapal bahkan bisa menghirup udara lewat pipa snorkel, sambil tetap berada dekat permukaan."),
            L("Saat menyelam, mesin diesel dimatikan. Motor listrik yang ditenagai baterai memutar baling-baling, nyaris tanpa suara."),
            L("Kelemahannya, baterai terbatas. Setelah beberapa hari, kapal harus kembali mengisi daya."),
            L("Sebagian kapal modern memakai sistem A-I-P, yaitu penggerak yang tidak membutuhkan udara dari luar, seperti sel bahan bakar, sehingga bisa tinggal di bawah air lebih lama.",
              "Sebagian kapal modern memakai sistem AIP, yaitu penggerak yang tidak membutuhkan udara dari luar, seperti sel bahan bakar, sehingga bisa tinggal di bawah air lebih lama."),
            L("Cara kedua adalah tenaga nuklir. Reaktor memanaskan air hingga menjadi uap, uap memutar turbin, dan turbin memutar baling-baling."),
            L("Pada desain modern, bahan bakar reaktor bisa bertahan puluhan tahun. Batas kapal nuklir bukan lagi bahan bakar, melainkan persediaan makanan untuk awaknya."),
            L("Baling-baling kapal selam juga dirancang khusus, melengkung dan miring, agar tidak mudah terdengar oleh lawan."),
        ],
    },
    {
        "id": "ch08", "file": "part3.py", "scene": "Ch08Life",
        "yt": "Bertahan hidup di kedalaman",
        "lines": [
            L("Di dalam tabung baja itu, manusia harus tetap bisa hidup."),
            L("Oksigen dibuat sendiri, lewat elektrolisis. Listrik dialirkan ke air, memecahnya menjadi oksigen dan hidrogen."),
            L("Oksigen dialirkan ke seluruh kapal, sementara hidrogen dibuang ke laut."),
            L("Karbon dioksida dari napas awak adalah masalah lain. Gas ini diserap oleh alat yang disebut skraber, sehingga udara tetap aman dihirup.",
              "Karbon dioksida dari napas awak adalah masalah lain. Gas ini diserap oleh alat yang disebut scrubber, sehingga udara tetap aman dihirup."),
            L("Air tawar juga dibuat dari air laut, lewat penyulingan atau osmosis balik."),
            L("Di kedalaman tidak ada siang dan malam. Dapur dan ruang mesin bekerja nyaris tanpa henti, dan awak bergantian berjaga dalam beberapa giliran."),
            L("Ruang sempit, lampu buatan, dan kerja bergilir menuntut ketahanan mental yang luar biasa."),
            L("Itu sebabnya awak kapal selam dipilih dan dilatih dengan sangat ketat."),
        ],
    },
    {
        "id": "ch09", "file": "part3.py", "scene": "Ch09Nav",
        "yt": "Navigasi dan sonar",
        "lines": [
            L("Di bawah laut, sinyal GPS tidak bisa menembus air, dan cahaya matahari lenyap dalam beberapa ratus meter.",
              "Di bawah laut, sinyal GPS tidak bisa menembus air, dan cahaya matahari lenyap dalam beberapa ratus meter."),
            L("Jadi bagaimana kapal selam tahu di mana ia berada?"),
            L("Jawabannya adalah navigasi inersia. Giroskop dan sensor percepatan mencatat setiap gerakan kapal, lalu komputer menghitung posisi barunya dari titik awal."),
            L("Sesekali, kapal naik mendekati permukaan untuk mengoreksi posisinya lewat satelit."),
            L("Untuk melihat sekitar, kapal selam mengandalkan sonar, singkatan dari sound navigation and ranging."),
            L("Sonar aktif mengirim pulsa suara, lalu mendengarkan gema yang memantul dari benda lain. Dari selang waktunya, jaraknya bisa dihitung."),
            L("Tapi sonar aktif membongkar posisi kapal itu sendiri. Karena itu, kapal selam lebih sering memakai sonar pasif, yang hanya mendengarkan, tanpa memancarkan apa pun."),
            L("Di laut, telinga lebih berharga daripada mata. Itulah sebabnya dunia kapal selam dijuluki dinas senyap."),
        ],
    },
    {
        "id": "ch10", "file": "part4.py", "scene": "Ch10Types",
        "yt": "Jenis-jenis kapal selam",
        "lines": [
            L("Tidak semua kapal selam sama."),
            L("Kapal selam serang bertugas memburu kapal lain dan melakukan pengintaian."),
            L("Kapal selam rudal balistik berpatroli diam-diam sebagai penangkal strategis, bersembunyi di kedalaman selama mungkin."),
            L("Ada pula kapal selam penelitian, yang dipakai menjelajah dasar laut, mengamati kapal karam, hingga meneliti makhluk laut dalam."),
            L("Contohnya Alvin, kapal selam kecil yang pernah menjelajah reruntuhan Titanic."),
            L("Ukurannya pun beragam, dari kapal kecil berawak dua atau tiga orang, sampai raksasa sepanjang lebih dari seratus meter."),
        ],
    },
    {
        "id": "ch11", "file": "part4.py", "scene": "Ch11Emergency",
        "yt": "Jika terjadi keadaan darurat",
        "lines": [
            L("Bagaimana jika sesuatu berjalan salah?"),
            L("Kapal selam punya sistem darurat. Salah satunya, meniup seluruh tangki ballast dengan udara bertekanan tinggi, agar kapal naik secepat mungkin."),
            L("Sebagian kapal juga bisa melepas pemberat tertentu untuk menambah daya apung."),
            L("Jika kapal tidak bisa naik, awak bisa memakai setelan penyelamat, keluar lewat ruang pelarian, lalu naik perlahan ke permukaan."),
            L("Ada pula kendaraan penyelamat khusus, yang menempel pada pintu kapal dan memindahkan awak dengan aman."),
            L("Latihan darurat dilakukan berulang kali, supaya setiap awak tahu persis apa yang harus dilakukan."),
        ],
    },
    {
        "id": "ch12", "file": "part4.py", "scene": "Ch12Outro",
        "yt": "Rangkuman dan penutup",
        "lines": [
            L("Mari kita rangkum."),
            L("Hukum Archimedes membuat sebuah benda bisa mengapung, melayang, atau tenggelam."),
            L("Tangki ballast mengatur berat, hidroplane mengatur arah, dan lambung tekan menahan raksasa tekanan laut."),
            L("Reaktor atau baterai memberi tenaga, sonar menjadi mata dan telinga, dan sistem pendukung kehidupan menjaga awak tetap hidup."),
            L("Jadi, setiap kali kapal selam menghilang di bawah ombak, kita sedang menyaksikan fisika sederhana, yang diterapkan dengan kecermatan luar biasa."),
            L("Kalau video ini membantumu memahami dunia sedikit lebih baik, tekan like, subscribe, dan tulis di kolom komentar, benda apa yang ingin kamu ketahui cara kerjanya berikutnya."),
            L("Sampai jumpa di video berikutnya, saat kita membongkar cara kerja hal menakjubkan lainnya."),
        ],
    },
]


def total_words():
    return sum(len(l["say"].split()) for c in CHAPTERS for l in c["lines"])
