เข้าใจแล้วครับ ✅
ถ้าคุณต้องการระบบแบบ **Single Admin Page** ใช้งานเอง ไม่ต้องซับซ้อนเหมือน WordPress ผมจะเขียน **SDD (Software Design Document) แบบย่อ** ที่ตอบโจทย์ดังนี้:

---

# 📑 Software Design Document (SDD)

## โครงการ: Mini CMS สำหรับองค์กร (Admin Page)

### 1. วัตถุประสงค์

* ให้ผู้ดูแล (admin) สามารถเข้าสู่ระบบ (login) เพื่อ **เพิ่ม/แก้ไข/ลบ ข่าวสาร และประกาศ** ได้
* ผู้ใช้ทั่วไป (public) เห็นหน้า **Dashboard/หน้าแรก** แสดงข่าวล่าสุด + ดาวน์โหลดไฟล์แนบได้
* ระบบเล็ก กระชับ ใช้ **FastAPI (Backend)** และ **Vue.js (Frontend)**

---

### 2. ขอบเขตการทำงาน (Scope)

1. **Public Site**

   * หน้า Dashboard แสดงข่าว/ประกาศ (title, content, date, attached files)
   * ปุ่ม/ลิงก์ดาวน์โหลดไฟล์แนบ
   * Pagination (เลื่อนดูข่าวย้อนหลังได้)

2. **Admin Site**

   * Login (Username/Password, JWT Auth)
   * จัดการข่าวสาร (Create/Read/Update/Delete)
   * อัปโหลดไฟล์แนบ (PDF, DOCX, XLSX, JPG, PNG)
   * Logout

---

### 3. ผู้ใช้ระบบ

* **Admin**: 1 คน (คุณ) → จัดการข่าวและประกาศ
* **Visitor**: ผู้เข้าชมทั่วไป → อ่านข่าว, ดาวน์โหลดไฟล์

---

### 4. สถาปัตยกรรมระบบ

* **Frontend (Vue.js + Vite + TailwindCSS)**

  * หน้า Public: `/` → แสดงข่าวทั้งหมด
  * หน้า Admin: `/admin/login`, `/admin/dashboard`, `/admin/news/edit/:id`
* **Backend (FastAPI)**

  * Auth: Login/Logout, JWT Token
  * News API: CRUD ข่าว + ไฟล์แนบ
  * Static File: เสิร์ฟไฟล์ดาวน์โหลด
* **Database (SQLite / PostgreSQL)**

  * ตาราง `users`, `news`, `files`
* **Deployment**: Docker Compose (1 container frontend, 1 backend, 1 DB)

---

### 5. โครงสร้างฐานข้อมูล (Schema)

**users**

* id (int, pk)
* username (str, unique)
* password\_hash (str)
* created\_at (datetime)

**news**

* id (int, pk)
* title (str)
* content (text)
* created\_at (datetime)
* updated\_at (datetime)

**files**

* id (int, pk)
* news\_id (fk → news.id)
* filename (str)
* filepath (str)
* uploaded\_at (datetime)

---

### 6. API Endpoints (FastAPI)

**Auth**

* `POST /api/login` → JWT Token
* `POST /api/logout`

**News (protected)**

* `GET /api/news` → list ข่าว (public)
* `GET /api/news/{id}` → รายละเอียดข่าว (public)
* `POST /api/news` → เพิ่มข่าว (admin)
* `PUT /api/news/{id}` → แก้ไขข่าว (admin)
* `DELETE /api/news/{id}` → ลบข่าว (admin)

**Files**

* `POST /api/news/{id}/files` → อัปโหลดไฟล์แนบ
* `GET /api/files/{id}` → ดาวน์โหลดไฟล์

---

### 7. UI/UX (Vue.js)

1. **Public Dashboard**

   * Card list ของข่าว
   * แสดง Title, Date, Short content
   * ปุ่ม "อ่านเพิ่มเติม" → ไปหน้า detail
   * ปุ่ม "ดาวน์โหลดไฟล์แนบ"

2. **Admin Login Page**

   * Form: username + password
   * เมื่อ login สำเร็จ → ไป `/admin/dashboard`

3. **Admin Dashboard**

   * Table list ข่าว
   * ปุ่ม: Add, Edit, Delete
   * Upload Attachments

---

### 8. ความปลอดภัย

* Password เก็บเป็น Hash (bcrypt)
* JWT Auth (Access + Refresh token)
* จำกัดไฟล์อัปโหลด (ตรวจ mime type + ขนาด < 20MB)

---

### 9. การติดตั้ง (Deployment)

* ใช้ Docker Compose
* Frontend (Vue build → serve static ผ่าน Nginx)
* Backend (FastAPI + Uvicorn)
* Database (SQLite → ง่ายสุด, หรือ PostgreSQL ถ้าต้อง scale)

---

👉 ระบบนี้เล็ก ใช้ได้จริง และดูแลเองง่าย ไม่ต้องมีปลั๊กอิน/ธีมเหมือน WordPress

---


