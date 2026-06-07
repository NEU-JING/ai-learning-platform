"""HTML templates used by service layer — extracted for readability."""

CERTIFICATE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>学习证书 - AI学习平台</title>
    <style>
        body {
            font-family: 'SimSun', serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
        }
        .certificate {
            width: 800px;
            background: white;
            padding: 60px;
            border: 20px solid #f0f0f0;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            position: relative;
        }
        .certificate::before {
            content: '';
            position: absolute;
            top: 10px;
            left: 10px;
            right: 10px;
            bottom: 10px;
            border: 2px solid #667eea;
        }
        .logo {
            font-size: 3rem;
            margin-bottom: 20px;
        }
        .title {
            font-size: 2.5rem;
            color: #333;
            margin-bottom: 10px;
            font-weight: bold;
        }
        .subtitle {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 40px;
        }
        .recipient {
            font-size: 2rem;
            color: #667eea;
            margin: 30px 0;
            font-weight: bold;
        }
        .course-name {
            font-size: 1.5rem;
            color: #333;
            margin: 20px 0;
        }
        .description {
            font-size: 1rem;
            color: #666;
            line-height: 1.8;
            margin: 30px 0;
        }
        .date {
            font-size: 1rem;
            color: #999;
            margin-top: 40px;
        }
        .signature {
            margin-top: 50px;
            display: flex;
            justify-content: space-between;
            padding: 0 50px;
        }
        .signature-item {
            text-align: center;
        }
        .signature-line {
            width: 150px;
            border-bottom: 2px solid #333;
            margin: 0 auto 10px;
            padding-bottom: 5px;
        }
        .signature-label {
            font-size: 0.9rem;
            color: #666;
        }
        .cert-id {
            position: absolute;
            bottom: 20px;
            right: 30px;
            font-size: 0.8rem;
            color: #999;
        }
        .badge {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 30px;
            border-radius: 25px;
            font-size: 1rem;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="certificate">
        <div class="logo">🎓</div>
        <div class="title">学习证书</div>
        <div class="subtitle">Certificate of Completion</div>

        <div style="font-size: 1rem; color: #666;">兹证明</div>
        <div class="recipient">{username}</div>

        <div class="description">
            已完成 <strong>AI学习平台</strong> 的<br>
            <span class="course-name">「{course_title}」</span><br>
            全部课程内容并通过考核
        </div>

        <div class="badge">{level_badge}</div>

        <div class="date">颁发日期：{issue_date}</div>

        <div class="signature">
            <div class="signature-item">
                <div class="signature-line"></div>
                <div class="signature-label">课程讲师</div>
            </div>
            <div class="signature-item">
                <div class="signature-line"></div>
                <div class="signature-label">平台认证</div>
            </div>
        </div>

        <div class="cert-id">证书编号：{cert_id}</div>
    </div>
</body>
</html>
"""
