export default {
  async fetch(request, env) {
    // 1. Cho phép CORS
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        }
      });
    }

    // 2. Test GET
    if (request.method === 'GET') {
      return new Response('FinSnap Worker is running! ✅', {
        headers: { 'Content-Type': 'text/plain' }
      });
    }

    // 3. Chỉ nhận POST
    if (request.method!== 'POST') {
      return new Response('Method Not Allowed', { status: 405 });
    }

    try {
      // 4. Lấy data từ frontend gửi lên
      const body = await request.json();

      const systemPrompt = `Bạn là chuyên gia tài chính nhưng giải thích cho người mới chơi chứng khoán F0-F2.
QUY TẮC: 1. CHỈ dùng số liệu được cung cấp. Cấm bịa. 2. Giọng GenZ, dễ hiểu. 3. Nếu có flags thì PHẢI nhắc rủi ro. 4. CẤM từ: mua, bán, khuyến nghị, nên đầu tư. 5. Luôn kết: "Cần theo dõi thêm báo cáo quý tới." 6. Output 2-3 câu.`;

      const userPrompt = `Mã: ${body.ticker} ${body.quarter}
Doanh thu: ${body.revenue}, Lợi nhuận: ${body.net_profit}
Nợ/Tài sản: ${body.debt_ratio}, Dòng tiền HĐKD: ${body.ocf} tỷ, ROE: ${body.roe}%
Điểm: ${body.score}/100, Cờ: ${body.flags?.join(', ') || 'Không'}`;

      const messages = [
        {"role": "system", "content": systemPrompt},
        {"role": "user", "content": userPrompt}
      ];

      // 5. Gọi OpenRouter
      const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${env.OPENROUTER_KEY}`,
          'HTTP-Referer': 'https://hung90909.github.io',
          'X-Title': 'FinSnap',
        },
        body: JSON.stringify({
          model: 'openrouter/free',
          messages: messages,
          temperature: 0.3,
          max_tokens: 150,
        })
      });

      const data = await response.json();

      // 6. Xử lý lỗi từ OpenRouter
      if (!response.ok) {
        return new Response(JSON.stringify({ error: data.error?.message || 'OpenRouter error' }), {
          status: 500,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
          }
        });
      }

      let text = data.choices?.[0]?.message?.content || 'Không có phản hồi từ AI';

      // 7. Filter từ cấm
      if (text.toLowerCase().includes('mua') || text.toLowerCase().includes('bán') || text.toLowerCase().includes('khuyến nghị')) {
        text = 'Công ty có điểm tốt và điểm cần lưu ý theo dữ liệu. Cần theo dõi thêm báo cáo quý tới.';
      }

      // 8. Trả về cho frontend
      return new Response(JSON.stringify({
        explanation: text.trim()
      }), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        }
      });

    } catch (error) {
      return new Response(JSON.stringify({
        error: 'Worker error: ' + error.message
      }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        }
      });
    }
  }
}
