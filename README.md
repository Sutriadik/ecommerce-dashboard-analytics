# Brazil E-Commerce Analytics Dashboard ✨

Dashboard interaktif analisis data e-commerce publik Brazil (Olist) menggunakan Streamlit.

**Nama:** Sutriadi Kurniawan  
**Email:** sutriadik@gmail.com  

---

## Pertanyaan Bisnis

1. Bagaimana performa tren penjualan bulanan secara historis?
2. Kategori produk apa yang laris dan menghasilkan revenue tertinggi?
3. Negara bagian mana yang memiliki performa penjualan tertinggi dan bagaimana persebaran geografis pelanggannya?
4. Bagaimana profil segmentasi pelanggan berdasarkan RFM Analysis?

---

## Struktur Direktori

```
submission/
├── dashboard/
│   ├── dashboard.py
│   └── main_data.csv
├── data/
├── notebook.ipynb
├── customers_dataset.csv
├── geolocation_dataset.csv
├── order_items_dataset.csv
├── order_payments_dataset.csv
├── orders_dataset.csv
├── product_category_name_translation.csv
├── products_dataset.csv
├── requirements.txt
└── README.md
```

---

## Setup Environment - Anaconda

```
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

---

## Notebook Analysis

File `notebook.ipynb` berisi proses analisis data secara lengkap mulai dari
*gathering data*, *assessing*, *cleaning*, *EDA*, hingga *visualisasi*.

Cara membuka notebook:

```
jupyter notebook notebook.ipynb
```

Atau buka langsung melalui **Google Colab** dengan mengupload file `notebook.ipynb`.

---

## Run Streamlit App

File `dashboard/dashboard.py` merupakan script dashboard interaktif yang dibangun
menggunakan Streamlit untuk menyajikan hasil analisis secara visual.

```
streamlit run dashboard/dashboard.py
```

---

## Live Dashboard

🔗 https://sutriadik24-ecommerce-dashboard.streamlit.app
