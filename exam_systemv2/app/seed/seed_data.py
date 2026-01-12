from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.repositories.user_repository import UserRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.exam_repository import ExamRepository
from app.repositories.assignment_repository import AssignmentRepository
from app.core.security import hash_password
from app.models.user import UserRole
from app.models.question import Question, QuestionOption, QuestionTag, QuestionType
from app.models.exam import Exam, ExamQuestion, ExamStatus, GradingPolicy
from app.models.assignment import Assignment
import random


# Türkçe isim ve soyisim listeleri
FIRST_NAMES = [
    "Ahmet", "Mehmet", "Ali", "Mustafa", "Hasan", "Hüseyin", "İbrahim", "İsmail",
    "Yusuf", "Ömer", "Osman", "Fatih", "Emre", "Can", "Burak", "Kerem", "Arda",
    "Ege", "Deniz", "Cem", "Onur", "Serkan", "Tolga", "Murat", "Kemal",
    "Ayşe", "Fatma", "Zeynep", "Elif", "Merve", "Selin", "Derya", "Burcu",
    "Gizem", "Seda", "Pınar", "Esra", "Özge", "Ceren", "Büşra", "Selin",
    "Melis", "Ece", "İrem", "Dilara", "Beren", "Defne", "Eda", "Gamze"
]

LAST_NAMES = [
    "Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Yıldız", "Yıldırım", "Öztürk",
    "Aydın", "Özdemir", "Arslan", "Doğan", "Kılıç", "Aslan", "Çetin", "Kara",
    "Koç", "Kurt", "Özkan", "Şimşek", "Polat", "Özkan", "Erdoğan", "Avcı",
    "Aksoy", "Ateş", "Bulut", "Çakır", "Duran", "Güler", "Işık", "Kılıç",
    "Özer", "Sarı", "Taş", "Türk", "Ünal", "Vural", "Yavuz", "Zengin",
    "Aktaş", "Başar", "Çağlar", "Duman", "Ertürk", "Güneş", "İpek", "Kartal"
]

# Öğretmenler ve dersleri
TEACHERS = [
    {"name": "Prof. Dr. Ayşe Yılmaz", "subject": "Matematik", "email": "ayse.yilmaz@bau.com"},
    {"name": "Doç. Dr. Mehmet Kaya", "subject": "Fizik", "email": "mehmet.kaya@bau.com"},
    {"name": "Dr. Öğr. Üyesi Zeynep Demir", "subject": "Kimya", "email": "zeynep.demir@bau.com"},
    {"name": "Prof. Dr. Ali Şahin", "subject": "Biyoloji", "email": "ali.sahin@bau.com"},
    {"name": "Doç. Dr. Fatma Çelik", "subject": "Türkçe", "email": "fatma.celik@bau.com"},
    {"name": "Dr. Öğr. Üyesi Mustafa Yıldız", "subject": "Tarih", "email": "mustafa.yildiz@bau.com"},
    {"name": "Prof. Dr. Elif Öztürk", "subject": "Coğrafya", "email": "elif.ozturk@bau.com"},
    {"name": "Doç. Dr. Hasan Aydın", "subject": "Felsefe", "email": "hasan.aydin@bau.com"},
    {"name": "Dr. Öğr. Üyesi Merve Arslan", "subject": "İngilizce", "email": "merve.arslan@bau.com"},
    {"name": "Prof. Dr. Emre Doğan", "subject": "Bilgisayar Bilimleri", "email": "emre.dogan@bau.com"}
]

# Sınav konuları ve soruları
EXAM_DATA = [
    {
        "name": "TYT Matematik Deneme Sınavı",
        "subject": "Matematik",
        "description": "Temel Yeterlilik Testi Matematik Deneme Sınavı",
        "duration": 60,
        "questions": [
            {
                "title": "İkinci Dereceden Denklem",
                "body": "x² - 5x + 6 = 0 denkleminin kökleri toplamı kaçtır?",
                "difficulty": 2,
                "options": [
                    {"text": "5", "is_correct": True},
                    {"text": "-5", "is_correct": False},
                    {"text": "6", "is_correct": False},
                    {"text": "-6", "is_correct": False}
                ],
                "explanation": "İkinci dereceden denklemde ax²+bx+c=0 formunda kökler toplamı -b/a'dır."
            },
            {
                "title": "Fonksiyon Değeri",
                "body": "f(x) = 2x + 3 fonksiyonu için f(5) değeri kaçtır?",
                "difficulty": 1,
                "options": [
                    {"text": "10", "is_correct": False},
                    {"text": "13", "is_correct": True},
                    {"text": "15", "is_correct": False},
                    {"text": "17", "is_correct": False}
                ],
                "explanation": "f(5) = 2(5) + 3 = 10 + 3 = 13"
            },
            {
                "title": "Üslü Sayılar",
                "body": "2³ × 2⁴ işleminin sonucu kaçtır?",
                "difficulty": 1,
                "options": [
                    {"text": "2⁷", "is_correct": True},
                    {"text": "2¹²", "is_correct": False},
                    {"text": "4⁷", "is_correct": False},
                    {"text": "8⁷", "is_correct": False}
                ],
                "explanation": "Aynı tabanlı üslü sayılar çarpılırken üsler toplanır: 2³ × 2⁴ = 2³⁺⁴ = 2⁷"
            },
            {
                "title": "Köklü Sayılar",
                "body": "√16 + √9 işleminin sonucu kaçtır?",
                "difficulty": 1,
                "options": [
                    {"text": "5", "is_correct": False},
                    {"text": "7", "is_correct": True},
                    {"text": "9", "is_correct": False},
                    {"text": "25", "is_correct": False}
                ],
                "explanation": "√16 = 4 ve √9 = 3, dolayısıyla 4 + 3 = 7"
            },
            {
                "title": "Oran-Orantı",
                "body": "Bir sınıfta kız ve erkek öğrenci sayısı 3:5 oranındadır. Sınıfta 24 kız öğrenci varsa, toplam öğrenci sayısı kaçtır?",
                "difficulty": 2,
                "options": [
                    {"text": "40", "is_correct": False},
                    {"text": "64", "is_correct": True},
                    {"text": "72", "is_correct": False},
                    {"text": "80", "is_correct": False}
                ],
                "explanation": "3k = 24 ise k = 8. Erkek sayısı = 5k = 40. Toplam = 24 + 40 = 64"
            },
            {
                "title": "Yüzde Hesaplama",
                "body": "Bir ürünün fiyatı %20 indirimle 80 TL'ye düşmüştür. Orijinal fiyatı kaç TL'dir?",
                "difficulty": 2,
                "options": [
                    {"text": "90", "is_correct": False},
                    {"text": "100", "is_correct": True},
                    {"text": "110", "is_correct": False},
                    {"text": "120", "is_correct": False}
                ],
                "explanation": "Orijinal fiyat x olsun. x × 0.8 = 80, dolayısıyla x = 100"
            },
            {
                "title": "Geometri - Alan",
                "body": "Bir dikdörtgenin uzun kenarı 12 cm, kısa kenarı 8 cm ise alanı kaç cm²'dir?",
                "difficulty": 1,
                "options": [
                    {"text": "80", "is_correct": False},
                    {"text": "96", "is_correct": True},
                    {"text": "100", "is_correct": False},
                    {"text": "120", "is_correct": False}
                ],
                "explanation": "Dikdörtgen alanı = uzun kenar × kısa kenar = 12 × 8 = 96 cm²"
            },
            {
                "title": "Permütasyon",
                "body": "5 farklı kitap bir rafa kaç farklı şekilde dizilebilir?",
                "difficulty": 3,
                "options": [
                    {"text": "60", "is_correct": False},
                    {"text": "120", "is_correct": True},
                    {"text": "240", "is_correct": False},
                    {"text": "720", "is_correct": False}
                ],
                "explanation": "5! = 5 × 4 × 3 × 2 × 1 = 120"
            },
            {
                "title": "Logaritma",
                "body": "log₂(8) değeri kaçtır?",
                "difficulty": 2,
                "options": [
                    {"text": "2", "is_correct": False},
                    {"text": "3", "is_correct": True},
                    {"text": "4", "is_correct": False},
                    {"text": "8", "is_correct": False}
                ],
                "explanation": "2³ = 8 olduğundan log₂(8) = 3"
            },
            {
                "title": "Trigonometri",
                "body": "sin(30°) değeri kaçtır?",
                "difficulty": 1,
                "options": [
                    {"text": "0", "is_correct": False},
                    {"text": "1/2", "is_correct": True},
                    {"text": "√2/2", "is_correct": False},
                    {"text": "√3/2", "is_correct": False}
                ],
                "explanation": "sin(30°) = 1/2"
            }
        ]
    },
    {
        "name": "TYT Fizik Deneme Sınavı",
        "subject": "Fizik",
        "description": "Temel Yeterlilik Testi Fizik Deneme Sınavı",
        "duration": 60,
        "questions": [
            {
                "title": "Hareket",
                "body": "Bir araç 60 km/h sabit hızla 2 saat yol alırsa, toplam kaç km yol alır?",
                "difficulty": 1,
                "options": [
                    {"text": "100", "is_correct": False},
                    {"text": "120", "is_correct": True},
                    {"text": "140", "is_correct": False},
                    {"text": "160", "is_correct": False}
                ],
                "explanation": "Yol = Hız × Zaman = 60 × 2 = 120 km"
            },
            {
                "title": "Kuvvet",
                "body": "Newton'un ikinci yasasına göre F = m × a formülünde F neyi temsil eder?",
                "difficulty": 1,
                "options": [
                    {"text": "Kuvvet", "is_correct": True},
                    {"text": "Kütle", "is_correct": False},
                    {"text": "İvme", "is_correct": False},
                    {"text": "Hız", "is_correct": False}
                ],
                "explanation": "F kuvveti, m kütleyi, a ise ivmeyi temsil eder."
            },
            {
                "title": "Enerji",
                "body": "Potansiyel enerji formülü nedir? (h: yükseklik, m: kütle, g: yerçekimi ivmesi)",
                "difficulty": 2,
                "options": [
                    {"text": "mgh", "is_correct": True},
                    {"text": "mgh²", "is_correct": False},
                    {"text": "mg/h", "is_correct": False},
                    {"text": "mh/g", "is_correct": False}
                ],
                "explanation": "Potansiyel enerji = m × g × h formülü ile hesaplanır."
            },
            {
                "title": "Elektrik",
                "body": "Ohm yasasına göre V = I × R formülünde V neyi temsil eder?",
                "difficulty": 1,
                "options": [
                    {"text": "Voltaj (Gerilim)", "is_correct": True},
                    {"text": "Akım", "is_correct": False},
                    {"text": "Direnç", "is_correct": False},
                    {"text": "Güç", "is_correct": False}
                ],
                "explanation": "V voltajı, I akımı, R ise direnci temsil eder."
            },
            {
                "title": "Dalga",
                "body": "Bir dalganın frekansı 50 Hz ise periyodu kaç saniyedir?",
                "difficulty": 2,
                "options": [
                    {"text": "0.01", "is_correct": False},
                    {"text": "0.02", "is_correct": True},
                    {"text": "0.05", "is_correct": False},
                    {"text": "0.1", "is_correct": False}
                ],
                "explanation": "T = 1/f = 1/50 = 0.02 saniye"
            },
            {
                "title": "Isı",
                "body": "Suyun kaynama noktası deniz seviyesinde kaç °C'dir?",
                "difficulty": 1,
                "options": [
                    {"text": "90", "is_correct": False},
                    {"text": "100", "is_correct": True},
                    {"text": "110", "is_correct": False},
                    {"text": "120", "is_correct": False}
                ],
                "explanation": "Deniz seviyesinde su 100°C'de kaynar."
            },
            {
                "title": "Manyetizma",
                "body": "Manyetik alan birimi nedir?",
                "difficulty": 2,
                "options": [
                    {"text": "Tesla", "is_correct": True},
                    {"text": "Volt", "is_correct": False},
                    {"text": "Amper", "is_correct": False},
                    {"text": "Watt", "is_correct": False}
                ],
                "explanation": "Manyetik alan birimi Tesla (T) veya Gauss'tur."
            },
            {
                "title": "Optik",
                "body": "Işığın boşluktaki hızı yaklaşık olarak kaç m/s'dir?",
                "difficulty": 1,
                "options": [
                    {"text": "3 × 10⁶", "is_correct": False},
                    {"text": "3 × 10⁸", "is_correct": True},
                    {"text": "3 × 10¹⁰", "is_correct": False},
                    {"text": "3 × 10¹²", "is_correct": False}
                ],
                "explanation": "Işığın boşluktaki hızı yaklaşık 3 × 10⁸ m/s'dir."
            },
            {
                "title": "Momentum",
                "body": "Momentum formülü nedir?",
                "difficulty": 1,
                "options": [
                    {"text": "p = mv", "is_correct": True},
                    {"text": "p = m/v", "is_correct": False},
                    {"text": "p = mv²", "is_correct": False},
                    {"text": "p = m²v", "is_correct": False}
                ],
                "explanation": "Momentum = kütle × hız = m × v"
            },
            {
                "title": "Basınç",
                "body": "Basınç formülü nedir? (F: kuvvet, A: alan)",
                "difficulty": 1,
                "options": [
                    {"text": "P = F/A", "is_correct": True},
                    {"text": "P = F × A", "is_correct": False},
                    {"text": "P = F/A²", "is_correct": False},
                    {"text": "P = F²/A", "is_correct": False}
                ],
                "explanation": "Basınç = Kuvvet / Alan = F/A"
            }
        ]
    },
    {
        "name": "TYT Kimya Deneme Sınavı",
        "subject": "Kimya",
        "description": "Temel Yeterlilik Testi Kimya Deneme Sınavı",
        "duration": 60,
        "questions": [
            {
                "title": "Periyodik Tablo",
                "body": "Periyodik tabloda kaç periyot vardır?",
                "difficulty": 1,
                "options": [
                    {"text": "5", "is_correct": False},
                    {"text": "6", "is_correct": False},
                    {"text": "7", "is_correct": True},
                    {"text": "8", "is_correct": False}
                ],
                "explanation": "Periyodik tabloda 7 periyot bulunur."
            },
            {
                "title": "Atom Yapısı",
                "body": "Bir atomun çekirdeğinde hangi parçacıklar bulunur?",
                "difficulty": 1,
                "options": [
                    {"text": "Proton ve nötron", "is_correct": True},
                    {"text": "Proton ve elektron", "is_correct": False},
                    {"text": "Nötron ve elektron", "is_correct": False},
                    {"text": "Sadece proton", "is_correct": False}
                ],
                "explanation": "Atom çekirdeğinde proton ve nötron bulunur, elektronlar çekirdek etrafında döner."
            },
            {
                "title": "Kimyasal Bağlar",
                "body": "İki atom arasında elektron paylaşımı ile oluşan bağ türü nedir?",
                "difficulty": 2,
                "options": [
                    {"text": "İyonik bağ", "is_correct": False},
                    {"text": "Kovalent bağ", "is_correct": True},
                    {"text": "Metalik bağ", "is_correct": False},
                    {"text": "Hidrojen bağı", "is_correct": False}
                ],
                "explanation": "Kovalent bağ, atomlar arasında elektron paylaşımı ile oluşur."
            },
            {
                "title": "Asit-Baz",
                "body": "pH değeri 7'den küçük olan çözeltiler nasıl adlandırılır?",
                "difficulty": 1,
                "options": [
                    {"text": "Bazik", "is_correct": False},
                    {"text": "Asidik", "is_correct": True},
                    {"text": "Nötr", "is_correct": False},
                    {"text": "Amfoter", "is_correct": False}
                ],
                "explanation": "pH < 7 asidik, pH = 7 nötr, pH > 7 bazik çözeltilerdir."
            },
            {
                "title": "Mol Kavramı",
                "body": "1 mol su (H₂O) kaç gramdır? (H: 1, O: 16)",
                "difficulty": 2,
                "options": [
                    {"text": "16", "is_correct": False},
                    {"text": "18", "is_correct": True},
                    {"text": "20", "is_correct": False},
                    {"text": "22", "is_correct": False}
                ],
                "explanation": "H₂O = 2(1) + 16 = 18 g/mol"
            },
            {
                "title": "Redoks",
                "body": "Elektron veren atom veya iyona ne denir?",
                "difficulty": 2,
                "options": [
                    {"text": "İndirgen", "is_correct": True},
                    {"text": "Yükseltgen", "is_correct": False},
                    {"text": "Katalizör", "is_correct": False},
                    {"text": "Elektrolit", "is_correct": False}
                ],
                "explanation": "Elektron veren indirgen, elektron alan yükseltgen olarak adlandırılır."
            },
            {
                "title": "Gazlar",
                "body": "İdeal gaz denklemi nedir?",
                "difficulty": 2,
                "options": [
                    {"text": "PV = nRT", "is_correct": True},
                    {"text": "PV = nR/T", "is_correct": False},
                    {"text": "P/V = nRT", "is_correct": False},
                    {"text": "PV² = nRT", "is_correct": False}
                ],
                "explanation": "İdeal gaz denklemi PV = nRT şeklindedir."
            },
            {
                "title": "Çözeltiler",
                "body": "100 mL suda 5 g tuz çözülürse, çözeltinin kütlece yüzde derişimi nedir?",
                "difficulty": 3,
                "options": [
                    {"text": "%4.76", "is_correct": True},
                    {"text": "%5", "is_correct": False},
                    {"text": "%10", "is_correct": False},
                    {"text": "%20", "is_correct": False}
                ],
                "explanation": "Toplam kütle = 100 + 5 = 105 g. Derişim = (5/105) × 100 = %4.76"
            },
            {
                "title": "Organik Kimya",
                "body": "Alkanların genel formülü nedir?",
                "difficulty": 2,
                "options": [
                    {"text": "CₙH₂ₙ₊₂", "is_correct": True},
                    {"text": "CₙH₂ₙ", "is_correct": False},
                    {"text": "CₙH₂ₙ₋₂", "is_correct": False},
                    {"text": "CₙHₙ", "is_correct": False}
                ],
                "explanation": "Alkanların genel formülü CₙH₂ₙ₊₂'dir."
            },
            {
                "title": "Termokimya",
                "body": "Ekzotermik reaksiyonlarda ne olur?",
                "difficulty": 1,
                "options": [
                    {"text": "Isı açığa çıkar", "is_correct": True},
                    {"text": "Isı soğurulur", "is_correct": False},
                    {"text": "Sıcaklık değişmez", "is_correct": False},
                    {"text": "Enerji korunur", "is_correct": False}
                ],
                "explanation": "Ekzotermik reaksiyonlarda ısı açığa çıkar, endotermik reaksiyonlarda ısı soğurulur."
            }
        ]
    },
    {
        "name": "TYT Biyoloji Deneme Sınavı",
        "subject": "Biyoloji",
        "description": "Temel Yeterlilik Testi Biyoloji Deneme Sınavı",
        "duration": 60,
        "questions": [
            {
                "title": "Hücre Yapısı",
                "body": "Ökaryot hücrelerde genetik materyal nerede bulunur?",
                "difficulty": 1,
                "options": [
                    {"text": "Sitoplazmada", "is_correct": False},
                    {"text": "Çekirdekte", "is_correct": True},
                    {"text": "Mitokondride", "is_correct": False},
                    {"text": "Ribozomda", "is_correct": False}
                ],
                "explanation": "Ökaryot hücrelerde DNA çekirdekte, prokaryot hücrelerde ise sitoplazmada bulunur."
            },
            {
                "title": "DNA Yapısı",
                "body": "DNA'nın yapı taşlarına ne denir?",
                "difficulty": 1,
                "options": [
                    {"text": "Amino asit", "is_correct": False},
                    {"text": "Nükleotid", "is_correct": True},
                    {"text": "Glukoz", "is_correct": False},
                    {"text": "Lipid", "is_correct": False}
                ],
                "explanation": "DNA'nın yapı taşları nükleotidlerdir."
            },
            {
                "title": "Fotosentez",
                "body": "Fotosentez hangi organelde gerçekleşir?",
                "difficulty": 1,
                "options": [
                    {"text": "Mitokondri", "is_correct": False},
                    {"text": "Kloroplast", "is_correct": True},
                    {"text": "Ribozom", "is_correct": False},
                    {"text": "Golgi", "is_correct": False}
                ],
                "explanation": "Fotosentez kloroplastlarda gerçekleşir."
            },
            {
                "title": "Sindirim",
                "body": "Proteinlerin sindirimi hangi organda başlar?",
                "difficulty": 2,
                "options": [
                    {"text": "Ağız", "is_correct": False},
                    {"text": "Mide", "is_correct": True},
                    {"text": "İnce bağırsak", "is_correct": False},
                    {"text": "Kalın bağırsak", "is_correct": False}
                ],
                "explanation": "Proteinlerin sindirimi midede pepsin enzimi ile başlar."
            },
            {
                "title": "Solunum",
                "body": "Oksijenli solunum hangi organelde gerçekleşir?",
                "difficulty": 1,
                "options": [
                    {"text": "Kloroplast", "is_correct": False},
                    {"text": "Mitokondri", "is_correct": True},
                    {"text": "Ribozom", "is_correct": False},
                    {"text": "Endoplazmik retikulum", "is_correct": False}
                ],
                "explanation": "Oksijenli solunum mitokondrilerde gerçekleşir."
            },
            {
                "title": "Genetik",
                "body": "İnsanda kaç kromozom çifti vardır?",
                "difficulty": 1,
                "options": [
                    {"text": "21", "is_correct": False},
                    {"text": "22", "is_correct": False},
                    {"text": "23", "is_correct": True},
                    {"text": "24", "is_correct": False}
                ],
                "explanation": "İnsanda 23 çift (46 adet) kromozom bulunur."
            },
            {
                "title": "Ekosistem",
                "body": "Besin zincirinde üreticilere ne denir?",
                "difficulty": 1,
                "options": [
                    {"text": "Birincil tüketici", "is_correct": False},
                    {"text": "İkincil tüketici", "is_correct": False},
                    {"text": "Ayrıştırıcı", "is_correct": False},
                    {"text": "Üretici (ototrof)", "is_correct": True}
                ],
                "explanation": "Besin zincirinde fotosentez yapan canlılar üretici (ototrof) olarak adlandırılır."
            },
            {
                "title": "Dolaşım Sistemi",
                "body": "İnsan kalbi kaç odacıklıdır?",
                "difficulty": 1,
                "options": [
                    {"text": "2", "is_correct": False},
                    {"text": "3", "is_correct": False},
                    {"text": "4", "is_correct": True},
                    {"text": "5", "is_correct": False}
                ],
                "explanation": "İnsan kalbi 4 odacıklıdır: 2 kulakçık, 2 karıncık."
            },
            {
                "title": "Sinir Sistemi",
                "body": "Sinir hücresine ne denir?",
                "difficulty": 1,
                "options": [
                    {"text": "Nöron", "is_correct": True},
                    {"text": "Nöroglia", "is_correct": False},
                    {"text": "Akson", "is_correct": False},
                    {"text": "Dendrit", "is_correct": False}
                ],
                "explanation": "Sinir hücresine nöron denir."
            },
            {
                "title": "Boşaltım",
                "body": "Böbreklerin temel işlev birimi nedir?",
                "difficulty": 2,
                "options": [
                    {"text": "Nefron", "is_correct": True},
                    {"text": "Glomerül", "is_correct": False},
                    {"text": "Tübül", "is_correct": False},
                    {"text": "Kapsül", "is_correct": False}
                ],
                "explanation": "Böbreklerin temel işlev birimi nefrondur."
            }
        ]
    },
    {
        "name": "TYT Türkçe Deneme Sınavı",
        "subject": "Türkçe",
        "description": "Temel Yeterlilik Testi Türkçe Deneme Sınavı",
        "duration": 60,
        "questions": [
            {
                "title": "Yazım Kuralları",
                "body": "Aşağıdakilerden hangisinde yazım hatası vardır?",
                "difficulty": 2,
                "options": [
                    {"text": "Her şey", "is_correct": False},
                    {"text": "Bir şey", "is_correct": False},
                    {"text": "Hiç bir şey", "is_correct": True},
                    {"text": "Herhangi bir şey", "is_correct": False}
                ],
                "explanation": "Doğru yazımı 'hiçbir şey' şeklindedir."
            },
            {
                "title": "Noktalama",
                "body": "Aşağıdaki cümlelerden hangisinde noktalama hatası vardır?",
                "difficulty": 2,
                "options": [
                    {"text": "Geldi, gördü, yendi.", "is_correct": False},
                    {"text": "Ona sordum; 'Nereye gidiyorsun?'", "is_correct": True},
                    {"text": "Kitap okumayı severim.", "is_correct": False},
                    {"text": "Ankara, Türkiye'nin başkentidir.", "is_correct": False}
                ],
                "explanation": "Soru işaretinden önce noktalı virgül değil, virgül kullanılmalıdır."
            },
            {
                "title": "Anlam Bilgisi",
                "body": "'Yakınmak' kelimesinin eş anlamlısı nedir?",
                "difficulty": 1,
                "options": [
                    {"text": "Şikayet etmek", "is_correct": True},
                    {"text": "Yaklaşmak", "is_correct": False},
                    {"text": "Yakmak", "is_correct": False},
                    {"text": "Yakalamak", "is_correct": False}
                ],
                "explanation": "'Yakınmak' kelimesi 'şikayet etmek' anlamına gelir."
            },
            {
                "title": "Dil Bilgisi",
                "body": "'Kitap okuyor' ifadesindeki 'okuyor' fiili hangi zamandadır?",
                "difficulty": 1,
                "options": [
                    {"text": "Geçmiş zaman", "is_correct": False},
                    {"text": "Şimdiki zaman", "is_correct": True},
                    {"text": "Gelecek zaman", "is_correct": False},
                    {"text": "Geniş zaman", "is_correct": False}
                ],
                "explanation": "'-yor' eki şimdiki zaman ekidir."
            },
            {
                "title": "Paragraf",
                "body": "Bir paragrafın ilk cümlesine ne denir?",
                "difficulty": 1,
                "options": [
                    {"text": "Giriş cümlesi", "is_correct": True},
                    {"text": "Gelişme cümlesi", "is_correct": False},
                    {"text": "Sonuç cümlesi", "is_correct": False},
                    {"text": "Ana cümle", "is_correct": False}
                ],
                "explanation": "Paragrafın ilk cümlesi giriş cümlesidir."
            },
            {
                "title": "Edebiyat",
                "body": "Divan edebiyatının en önemli şairi kimdir?",
                "difficulty": 2,
                "options": [
                    {"text": "Yunus Emre", "is_correct": False},
                    {"text": "Fuzuli", "is_correct": True},
                    {"text": "Karacaoğlan", "is_correct": False},
                    {"text": "Pir Sultan Abdal", "is_correct": False}
                ],
                "explanation": "Fuzuli, Divan edebiyatının en önemli şairlerinden biridir."
            },
            {
                "title": "Anlatım",
                "body": "Bir olayı zaman sırasına göre anlatma biçimine ne denir?",
                "difficulty": 1,
                "options": [
                    {"text": "Betimleme", "is_correct": False},
                    {"text": "Öyküleme", "is_correct": True},
                    {"text": "Açıklama", "is_correct": False},
                    {"text": "Tartışma", "is_correct": False}
                ],
                "explanation": "Olayları zaman sırasına göre anlatma biçimi öykülemedir."
            },
            {
                "title": "Kelime Türü",
                "body": "'Güzel' kelimesi hangi kelime türüne girer?",
                "difficulty": 1,
                "options": [
                    {"text": "İsim", "is_correct": False},
                    {"text": "Sıfat", "is_correct": True},
                    {"text": "Zarf", "is_correct": False},
                    {"text": "Fiil", "is_correct": False}
                ],
                "explanation": "'Güzel' kelimesi sıfattır, isimleri niteleyen kelimelerdir."
            },
            {
                "title": "Cümle Çeşitleri",
                "body": "'Kitap okuyor ve müzik dinliyor.' cümlesi hangi cümle türüne girer?",
                "difficulty": 2,
                "options": [
                    {"text": "Basit cümle", "is_correct": False},
                    {"text": "Birleşik cümle", "is_correct": False},
                    {"text": "Sıralı cümle", "is_correct": True},
                    {"text": "Bağlı cümle", "is_correct": False}
                ],
                "explanation": "Bağlaçla bağlanmış iki yargı sıralı cümle oluşturur."
            },
            {
                "title": "Anlatım Bozukluğu",
                "body": "Aşağıdakilerden hangisinde anlatım bozukluğu vardır?",
                "difficulty": 3,
                "options": [
                    {"text": "Kitabı okudum ve beğendim.", "is_correct": False},
                    {"text": "Ona sordum ve cevap verdi.", "is_correct": False},
                    {"text": "Herkes geldi ve toplantı başladı.", "is_correct": False},
                    {"text": "Kitabı okudum ve çok güzeldi.", "is_correct": True}
                ],
                "explanation": "Son cümlede özne-yüklem uyumsuzluğu vardır."
            }
        ]
    }
]


def generate_student_username(first_name: str, last_name: str, index: int) -> str:
    """Generate unique username from name."""
    base = f"{first_name.lower()}.{last_name.lower()}"
    return f"{base}{index}" if index > 0 else base


def seed_data():
    """Seed initial data with realistic Turkish data."""
    db: Session = SessionLocal()
    
    try:
        user_repo = UserRepository(db)
        question_repo = QuestionRepository(db)
        exam_repo = ExamRepository(db)
        assignment_repo = AssignmentRepository(db)
        
        # Create admin
        admin = user_repo.get_by_username("admin")
        if not admin:
            admin = user_repo.create(
                username="admin",
                password_hash=hash_password("admin123"),
                role=UserRole.ADMIN,
                email="admin@bau.com"
            )

         Demo users (for QA Automation)
        demo_users = [
           ("teacher",  "teacher123", UserRole.TEACHER, "teacher@bau.com"),
          ("student1", "student123", UserRole.STUDENT, "student1@bau.com"),
        ]
        for username, pw, role, email in demo_users:
            if not user_repo.get_by_username(username):
                user_repo.create(
                    username=username,
                    password_hash=hash_password(pw),
                    role=role,
                    email=email
                )
        db.commit()

        # Create teachers
        teachers = []
        for teacher_data in TEACHERS:
            # Extract name parts for username
            name_parts = teacher_data["name"].lower().split()
            # Remove titles and get first and last name
            name_parts = [p for p in name_parts if p not in ["prof.", "dr.", "doç.", "öğr.", "üyesi"]]
            if len(name_parts) >= 2:
                username = f"{name_parts[0]}.{name_parts[-1]}"
            else:
                username = ".".join(name_parts)
            
            teacher = user_repo.get_by_username(username)
            if not teacher:
                teacher = user_repo.create(
                    username=username,
                    password_hash=hash_password("ogretmen123"),
                    role=UserRole.TEACHER,
                    email=teacher_data["email"]
                )
            teachers.append(teacher)
        
        db.commit()
        
        # Create 100 students
        students = []
        used_names = set()
        for i in range(100):
            # Generate unique name combination
            while True:
                first_name = random.choice(FIRST_NAMES)
                last_name = random.choice(LAST_NAMES)
                name_key = f"{first_name} {last_name}"
                if name_key not in used_names:
                    used_names.add(name_key)
                    break
            
            username = generate_student_username(first_name, last_name, i if name_key in used_names else 0)
            email = f"{first_name.lower()}.{last_name.lower()}@bau.com"
            
            student = user_repo.get_by_username(username)
            if not student:
                student = user_repo.create(
                    username=username,
                    password_hash=hash_password("ogrenci123"),
                    role=UserRole.STUDENT,
                    email=email
                )
            students.append(student)
        
        db.commit()
        
        # Create exams with questions
        exams = []
        for exam_data in EXAM_DATA:
            # Find teacher for this subject
            teacher = next((t for t in teachers if exam_data["subject"] in TEACHERS[teachers.index(t)]["subject"]), teachers[0])
            if not teacher:
                teacher = teachers[0]
            
            # Find matching teacher by subject
            for idx, t_data in enumerate(TEACHERS):
                if exam_data["subject"] == t_data["subject"]:
                    teacher = teachers[idx]
                    break
            
            exam = Exam(
                owner_id=teacher.id,
                name=exam_data["name"],
                description=exam_data["description"],
                duration_minutes=exam_data["duration"],
                attempts_allowed=1,
                shuffle_questions=False,
                shuffle_options=False,
                grading_policy=GradingPolicy.IMMEDIATE,
                status=ExamStatus.PUBLISHED
            )
            exam = exam_repo.create(exam)
            
            # Add questions to exam
            created_questions = []
            for q_data in exam_data["questions"]:
                question = Question(
                    owner_id=teacher.id,
                    title=q_data["title"],
                    body=q_data["body"],
                    difficulty=q_data["difficulty"],
                    type=QuestionType.MULTIPLE_CHOICE,
                    explanation=q_data.get("explanation", "")
                )
                question = question_repo.create(question)
                
                # Add options
                for opt_data in q_data["options"]:
                    option = QuestionOption(
                        question_id=question.id,
                        text=opt_data["text"],
                        is_correct=1 if opt_data["is_correct"] else 0
                    )
                    db.add(option)
                
                # Add tags
                tag = QuestionTag(question_id=question.id, tag=exam_data["subject"].lower())
                db.add(tag)
                
                created_questions.append(question)
            
            db.commit()
            
            # Link questions to exam
            for idx, question in enumerate(created_questions, 1):
                exam_question = ExamQuestion(
                    exam_id=exam.id,
                    question_id=question.id,
                    sort_order=idx,
                    points=10
                )
                exam_repo.add_exam_question(exam_question)
            
            exams.append(exam)
            db.commit()
        
        # Assign exams to random students
        for exam in exams:
            # Assign to 20-30 random students
            num_assignments = random.randint(20, 30)
            selected_students = random.sample(students, min(num_assignments, len(students)))
            
            for student in selected_students:
                # Check if assignment already exists
                existing = assignment_repo.get_by_exam_and_student(exam.id, student.id)
                if not existing:
                    assignment = Assignment(
                        exam_id=exam.id,
                        student_id=student.id
                    )
                    assignment_repo.create(assignment)
        
        db.commit()
        
        print("=" * 60)
        print("Seed data created successfully!")
        print("=" * 60)
        print(f"\nUsers created:")
        print(f"  - 1 Admin: admin / admin123")
        print(f"  - {len(teachers)} Teachers: username / ogretmen123")
        print(f"  - {len(students)} Students: username / ogrenci123")
        print(f"\nExams created: {len(exams)}")
        for exam in exams:
            print(f"  - {exam.name} ({exam_repo.get_exam_questions(exam.id).__len__()} questions)")
        print(f"\nTotal assignments: {db.query(Assignment).count()}")
        print("\n" + "=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
