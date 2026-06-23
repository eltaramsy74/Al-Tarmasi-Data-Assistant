import os
import sys
import subprocess

# تحديد مسار الأناكوندا المستقر على جهازك بالملي
anaconda_python = r"C:\ProgramData\anaconda3\python.exe"
if not os.path.exists(anaconda_python):
    # مسار بديل لو متثبتة للمستخدم الحالي بس
    user_home = os.path.expanduser("~")
    anaconda_python = os.path.join(user_home, "anaconda3", "python.exe")

if __name__ == "__main__":
    # لو المسار المضمون بتاع الأناكوندا موجود، هيشغل البوت منه عل طول ويهرب من بايثون 3.14
    if os.path.exists(anaconda_python):
        print("🚀 تشغيل البوت عبر بيئة الأناكوندا المستقرة...")
        subprocess.run([anaconda_python, "-m", "streamlit", "run", "app.py"])
    else:
        # حل احتياطي لو ملقاش الأناكوندا خالص
        import streamlit.web.cli as stcli
        sys.argv = ["streamlit", "run", "app.py"]
        sys.exit(stcli.main())