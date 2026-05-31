from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app) # Tarayıcı engelini tamamen kaldırmak için

# Senin hazırladığın Jindex Studio HTML kodunu buraya gömüyoruz
HTML_PANEL = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jindex Studio | Sunucu Paneli</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #0b0c0e; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #16181c; }
        ::-webkit-scrollbar-thumb { background: #2c3036; border-radius: 10px; }
        .fade-in { animation: fadeIn 0.6s ease-out forwards; }
        .slide-up { animation: slideUp 0.4s ease-out forwards; }
        @keyframes fadeIn { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }
        @keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body class="text-zinc-200 min-h-screen flex items-center justify-center p-4 selection:bg-zinc-700 selection:text-white">

    <div class="fade-in max-w-md w-full bg-[#121418] border border-zinc-800/60 rounded-2xl p-6 shadow-2xl shadow-black/40">
        <div class="text-center mb-8">
            <h1 class="text-xl font-semibold tracking-wide text-white">JINDEX STUDIO</h1>
            <p class="text-xs text-zinc-500 mt-1 uppercase tracking-widest font-medium">SMS Request System v2026</p>
        </div>

        <div class="space-y-4">
            <div>
                <label class="block text-xs font-medium text-zinc-400 mb-1.5 ml-1">Hedef Telefon Numarası</label>
                <input type="text" id="phoneInput" placeholder="5xxxxxxxx" maxlength="10"
                       class="w-full bg-[#181a20] border border-zinc-800 focus:border-zinc-600 rounded-xl px-4 py-3 text-sm text-white placeholder-zinc-600 outline-none transition-all duration-300 tracking-wider">
            </div>

            <button id="startBtn" onclick="startProcess()"
                    class="w-full bg-zinc-100 hover:bg-white text-zinc-950 font-medium text-sm py-3 px-4 rounded-xl transition-all duration-300 cursor-pointer shadow-lg shadow-white/5 active:scale-[0.99]">
                Sistemi Başlat
            </button>
        </div>

        <div id="monitorArea" class="hidden mt-8 border-t border-zinc-800/80 pt-6">
            <div class="flex items-center justify-between mb-3 px-1">
                <span class="text-xs font-semibold tracking-wider text-zinc-400 uppercase flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    Canlı İzleme Monitörü
                </span>
                <span id="loader" class="text-[11px] text-zinc-500 font-medium">İstekler gönderiliyor...</span>
            </div>
            <div id="logConsole" class="w-full h-48 bg-[#181a20] border border-zinc-800/50 rounded-xl p-3 overflow-y-auto space-y-2 flex flex-col"></div>
        </div>

        <div class="mt-8 text-center">
            <p class="text-[10px] text-zinc-600 font-medium tracking-wide">&copy; 2026 Jindex Studio. Tüm hakları saklıdır.</p>
        </div>
    </div>

    <script>
        function logMessage(msg, type) {
            const logConsole = document.getElementById("logConsole");
            const logRow = document.createElement("div");
            logRow.className = "slide-up text-xs font-mono py-1 px-2.5 rounded-md flex items-center justify-between transition-all duration-300";
            if (type === "success") {
                logRow.className += " bg-zinc-900/40 text-emerald-400 border-l-2 border-emerald-500";
            } else {
                logRow.className += " bg-zinc-950/20 text-rose-500 border-l-2 border-rose-800";
            }
            logRow.innerText = msg;
            logConsole.appendChild(logRow);
            logConsole.scrollTo({ top: logConsole.scrollHeight, behavior: 'smooth' });
        }

        async function startProcess() {
            const phoneInput = document.getElementById("phoneInput");
            const startBtn = document.getElementById("startBtn");
            const monitorArea = document.getElementById("monitorArea");
            const logConsole = document.getElementById("logConsole");
            const loader = document.getElementById("loader");

            if (phoneInput.value.length !== 10) {
                alert("Lütfen numarayı başında 0 olmadan 10 hane olarak girin.");
                return;
            }

            phoneInput.disabled = true;
            startBtn.disabled = true;
            startBtn.classList.add("opacity-50", "cursor-not-allowed");
            logConsole.innerHTML = "";
            monitorArea.classList.remove("hidden");
            loader.innerText = "Sistem tetiklendi, istekler Python üzerinden atılıyor...";
            loader.className = "text-[11px] text-zinc-500 font-medium animate-pulse";

            const phone = phoneInput.value;

            try {
                // İsteyi doğrudan arka plandaki Python API'sine gönderiyoruz
                let response = await fetch('/api/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone: phone })
                });
                let result = await response.json();
                
                // Python'dan dönen servis sonuçlarını ekrana basıyoruz
                if(result.status === "started") {
                    result.logs.forEach(log => {
                        logMessage(log.msg, log.type);
                    });
                }
            } catch (e) {
                logMessage("Sistem hatası: Sunucuya bağlanılamadı.", "fail");
            }

            loader.innerText = "Tamamlandı";
            loader.classList.remove("animate-pulse");
            loader.classList.add("text-emerald-400");
            startBtn.disabled = false;
            startBtn.classList.remove("opacity-50", "cursor-not-allowed");
            phoneInput.disabled = false;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    # Tarayıcıdan girildiğinde direkt paneli açar
    return render_template_string(HTML_PANEL)

@app.route('/api/start', str_methods=['POST']) # Not: Mevcut smscy yapına entegre endpoint
def start_sms():
    data = request.json
    phone = data.get("phone")
    
    if not phone or len(phone) != 10:
        return jsonify({"status": "error", "message": "Geçersiz numara"}), 400

    # Bu kısımda senin smscy.py içindeki SendSms sınıfını tetikliyoruz
    # Rastgele bir mail üretiyoruz
    import random
    letters = 'abcdefghijklmnopqrstuvwxyz'
    mail = "".join(random.choice(letters) for _ in range(22)) + "@gmail.com"
    
    # Senin mevcut sms sınıfın (SendSms sınıfının adının ve yapısının böyle olduğunu varsayıyorum)
    # Eğer sınıf adı farklıysa burayı o isme göre güncelle
    send_sms = SendSms(phone, mail)
    
    logs = []
    
    # Senin 'servisler_sms' listendeki tüm fonksiyonları sırayla çalıştırıp log topluyoruz
    for fonk_adi in servisler_sms:
        try:
            # Fonksiyonu dinamik çağırıyoruz (getattr ile)
            fonksiyon = getattr(send_sms, fonk_adi)
            fonksiyon() # İsteği atar (Python attığı için CORS falan dinlemez, tıkır tıkır gider)
            logs.append({"msg": f"Başarılı! {phone} --> {fonk_adi}", "type": "success"})
        except Exception as e:
            logs.append({"msg": f"Başarısız! {phone} --> {fonk_adi}", "type": "fail"})
            
    return jsonify({"status": "started", "logs": logs})

if __name__ == '__main__':
    # Sunucuyu yerelde 5000 portunda başlatıyoruz
    app.run(host='0.0.0.0', port=5000, debug=True)
