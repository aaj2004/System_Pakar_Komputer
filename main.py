from flask import Flask, render_template, request

app = Flask(__name__)

# Basis Pengetahuan
# Gejala diperbanyak
gejala = {
    "G01": "Layar tidak menyala",
    "G02": "Komputer tidak bisa booting",
    "G03": "Kipas tidak berputar",
    "G04": "Muncul suara beep",
    "G05": "Harddisk tidak terdeteksi",
    "G06": "Lampu indikator mati",
    "G07": "Suara kipas berisik",
    "G08": "Tampilan layar berkedip",
    "G09": "Windows sering hang",
    "G10": "Komputer restart sendiri",
    "G11": "Port USB tidak berfungsi",
    "G12": "Mouse dan keyboard tidak merespon",
    "G13": "Sistem lambat saat booting",
    "G14": "Tidak ada suara dari speaker",
    "G15": "Baterai laptop cepat habis",
    "G16": "Overheating (panas berlebihan)",
    "G17": "Wifi tidak terdeteksi",
    "G18": "Port charger tidak mengisi daya",
    "G19": "Blue screen muncul saat startup",
    "G20": "Tombol power tidak berfungsi"
}

# Kerusakan diperbanyak dan lebih spesifik
kerusakan = {
    "K01": "Kerusakan Power Supply",
    "K02": "Kerusakan RAM",
    "K03": "Kerusakan Harddisk",
    "K04": "Kerusakan Motherboard",
    "K05": "Kerusakan VGA Card",
    "K06": "Kerusakan Sistem Operasi",
    "K07": "Kerusakan Baterai Laptop",
    "K08": "Kerusakan Keyboard/Mouse",
    "K09": "Kerusakan Pendingin/Kipas",
    "K10": "Kerusakan Charger/Laptop Charging Port"
}

# Rules backward chaining dengan gejala lebih lengkap
rules_cf = {
    "K01": [("G01", 0.8), ("G06", 0.9), ("G20", 0.85)],
    "K02": [("G02", 0.9), ("G04", 0.7), ("G19", 0.9), ("G10", 0.6)],
    "K03": [("G05", 0.9), ("G09", 0.7), ("G13", 0.8)],
    "K04": [("G03", 0.85), ("G07", 0.75), ("G08", 0.8), ("G16", 0.7)],
    "K05": [("G08", 0.9), ("G14", 0.85), ("G19", 0.8)],
    "K06": [("G09", 0.8), ("G19", 0.9), ("G13", 0.75), ("G10", 0.7)],
    "K07": [("G15", 0.95), ("G18", 0.9), ("G20", 0.5)],
    "K08": [("G11", 0.8), ("G12", 0.85)],
    "K09": [("G07", 0.9), ("G03", 0.8), ("G16", 0.85)],
    "K10": [("G18", 0.95), ("G20", 0.6)]
}


def hitung_cf(user_input):
    hasil = {}
    for k, aturan in rules_cf.items():
        cf_list = []
        for g, cf_rule in aturan:
            cf_user = float(user_input.get(g, 0))
            cf_hasil = cf_user * cf_rule
            if cf_hasil > 0:
                cf_list.append(cf_hasil)
        if cf_list:
            cf_final = cf_list[0]
            for cf in cf_list[1:]:
                cf_final = cf_final + cf * (1 - cf_final)
            hasil[k] = round(cf_final, 3)
    return hasil

@app.route('/', methods=['GET', 'POST'])
def index():
    hasil = None
    if request.method == 'POST':
        input_cf = {key: request.form.get(key, type=float) for key in gejala}
        hasil = hitung_cf(input_cf)
        hasil = sorted(hasil.items(), key=lambda x: x[1], reverse=True)
    return render_template('index.html', gejala=gejala, hasil=hasil, kerusakan=kerusakan)

@app.route('/forward', methods=['GET', 'POST'])
def forward():
    hasil = []
    if request.method == 'POST':
        gejala_user = [k for k in gejala if request.form.get(k)]

        for kode, aturan in rules_cf.items():
            total_cf = 0
            total_rule = len(aturan)
            if total_rule == 0:
                continue
            matched = [cf for g, cf in aturan if g in gejala_user]
            if matched:
                cf_score = (sum(matched) / sum(cf for _, cf in aturan)) * 100
                hasil.append({'nama': kerusakan[kode], 'cf': round(cf_score, 2)})

        # Urutkan dari nilai CF terbesar
        hasil = sorted(hasil, key=lambda x: x['cf'], reverse=True)

    return render_template('forward.html', gejala=gejala, hasil=hasil)


@app.route('/backward', methods=['GET', 'POST'])
def backward():
    selected = None
    hasil = None

    if request.method == 'POST':
        selected = request.form.get('kerusakan')
        if selected:
            # Ambil aturan gejala dari kerusakan yang dipilih
            aturan = rules_cf.get(selected, [])
            gejala_input = [g for g, _ in aturan if request.form.get(g)]

            if aturan:
                total_cf = sum(cf for _, cf in aturan)
                matched_cf = sum(cf for g, cf in aturan if g in gejala_input)

                persen = (matched_cf / total_cf) * 100 if total_cf > 0 else 0
                if persen >= 70:
                    hasil = f"✅ Kemungkinan besar kerusakan: {kerusakan[selected]} ({round(persen, 2)}%)"
                elif persen > 0:
                    hasil = f"⚠️ Kemungkinan kerusakan: {kerusakan[selected]} ({round(persen, 2)}%)"
                else:
                    hasil = f"❌ Gejala tidak cocok dengan kerusakan {kerusakan[selected]}"
    
    return render_template(
        'backward.html',
        kerusakan=kerusakan,
        gejala=gejala,
        rules_cf=rules_cf,
        selected=selected,
        hasil=hasil
    )


if __name__ == '__main__':
    app.run(debug=True)

