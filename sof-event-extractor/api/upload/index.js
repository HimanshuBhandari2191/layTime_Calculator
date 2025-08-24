import formidable from "formidable";

export default async function (context, req) {
  if (req.method === "OPTIONS") {
    context.res = {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
      }
    };
    return;
  }

  if (req.method !== "POST") {
    context.res = { status: 405, body: "Method Not Allowed" };
    return;
  }

  try {
    const form = formidable({ multiples: false, keepExtensions: true });
    const { fields, files } = await new Promise((resolve, reject) =>
      form.parse(req, (err, fields, files) => (err ? reject(err) : resolve({ fields, files })))
    );

    const file = files.file || files.upload || Object.values(files)[0];
    if (!file) {
      context.res = { status: 400, body: "No file received" };
      return;
    }

    context.res = {
      status: 200,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
      body: {
        message: "Upload successful",
        originalFilename: file.originalFilename,
        size: file.size
      }
    };
  } catch (err) {
    context.log("Upload error:", err);
    context.res = { status: 500, body: "Upload failed" };
  }
}
