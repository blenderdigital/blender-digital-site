const crypto = require("crypto");

function send(res, status, body) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify(body));
}

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    return send(res, 405, { ok: false });
  }

  try {
    const { email, name, annualSales, locations, notes, source } = req.body || {};

    if (!email) {
      return send(res, 400, { ok: false, error: "Email required" });
    }

    const API_KEY = process.env.MAILCHIMP_API_KEY;
    const SERVER = process.env.MAILCHIMP_SERVER_PREFIX;
    const LIST_ID = process.env.MAILCHIMP_AUDIENCE_ID;

    const hash = crypto
      .createHash("md5")
      .update(email.toLowerCase())
      .digest("hex");

    const url = `https://${SERVER}.api.mailchimp.com/3.0/lists/${LIST_ID}/members/${hash}`;

    const payload = {
      email_address: email,
      status_if_new: "subscribed",
      merge_fields: {
        ANSALES: annualSales || "",
        LOCNUM: locations || "",
        NOTES: notes || "",
        SOURCE: source || "",
      },
    };

    if (name) {
      payload.merge_fields.NOTES =
        `Name: ${name}\n\n` + payload.merge_fields.NOTES;
    }

    const response = await fetch(url, {
      method: "PUT",
      headers: {
        Authorization:
          "Basic " +
          Buffer.from("anystring:" + API_KEY).toString("base64"),
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      return send(res, 400, { ok: false });
    }

    return send(res, 200, { ok: true });
  } catch (e) {
    return send(res, 500, { ok: false });
  }
};
