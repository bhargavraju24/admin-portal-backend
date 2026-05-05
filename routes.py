from flask import request, jsonify, render_template
from models import db, Admin, Opportunity
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer

serializer = URLSafeTimedSerializer("mysecretkey")


def register_routes(app):

    # HOME
    @app.route("/")
    def home():
        return render_template("admin.html")

    # SIGNUP
    @app.route("/signup", methods=["POST"])
    def signup():
        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        confirm = data.get("confirmPassword")

        if not all([name, email, password, confirm]):
            return jsonify({"message": "All fields are required"}), 400

        if len(password) < 8:
            return jsonify({"message": "Password must be at least 8 characters"}), 400

        if password != confirm:
            return jsonify({"message": "Passwords do not match"}), 400

        if Admin.query.filter_by(email=email).first():
            return jsonify({"message": "Email already exists"}), 400

        hashed = generate_password_hash(password)

        user = Admin(name=name, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Signup successful"}), 200

    # LOGIN
    @app.route("/login", methods=["POST"])
    def login():
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"message": "Email and password required"}), 400

        user = Admin.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({"message": "Invalid email or password"}), 401

        return jsonify({
            "message": "Login successful",
            "adminId": user.id
        }), 200

    # FORGOT PASSWORD
    @app.route("/forgot-password", methods=["POST"])
    def forgot_password():
        data = request.get_json()
        email = data.get("email")

        user = Admin.query.filter_by(email=email).first()

        if user:
            token = serializer.dumps(email, salt="reset-password")
            reset_link = f"http://127.0.0.1:5000/reset-password/{token}"
            print("RESET LINK:", reset_link)

        return jsonify({
            "message": "If email exists, reset link sent"
        }), 200

    # DASHBOARD
    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

   
    # OPPORTUNITY APIs
   

    # ADD
    @app.route("/opportunities", methods=["POST"])
    def add_opportunity():
        data = request.get_json()

        opp = Opportunity(
            name=data.get("name"),
            duration=data.get("duration"),
            start_date=data.get("startDate"),
            description=data.get("description"),
            skills=",".join(data.get("skills", [])),
            category=data.get("category"),
            future=data.get("futureOpportunities"),
            max_applicants=data.get("maxApplicants"),
            admin_id=data.get("adminId")
        )

        db.session.add(opp)
        db.session.commit()

        return jsonify({"success": True})

    # GET ALL
    @app.route("/opportunities/<int:admin_id>", methods=["GET"])
    def get_opportunities(admin_id):
        opps = Opportunity.query.filter_by(admin_id=admin_id).all()

        return jsonify([
            {
                "id": o.id,
                "name": o.name,
                "description": o.description,
                "duration": o.duration,
                "startDate": o.start_date,
                "category": o.category
            }
            for o in opps
        ])

    # GET SINGLE
    @app.route("/opportunity/<int:id>", methods=["GET"])
    def get_opportunity(id):
        o = Opportunity.query.get(id)

        return jsonify({
            "id": o.id,
            "name": o.name,
            "description": o.description,
            "duration": o.duration,
            "startDate": o.start_date,
            "category": o.category,
            "skills": o.skills.split(",") if o.skills else [],
            "futureOpportunities": o.future,
            "applicants": o.max_applicants or 0
        })

    # DELETE
    @app.route("/opportunity/<int:id>", methods=["DELETE"])
    def delete_opportunity(id):
        o = Opportunity.query.get(id)

        if not o:
            return jsonify({"message": "Not found"}), 404

        db.session.delete(o)
        db.session.commit()

        return jsonify({"success": True})

    # UPDATE (EDIT) 
    @app.route("/opportunity/<int:id>", methods=["PUT"])
    def update_opportunity(id):
        data = request.get_json()

        opp = Opportunity.query.get(id)

        if not opp:
            return jsonify({"message": "Not found"}), 404

        opp.name = data.get("name")
        opp.duration = data.get("duration")
        opp.start_date = data.get("startDate")
        opp.description = data.get("description")
        opp.skills = ",".join(data.get("skills", []))
        opp.category = data.get("category")
        opp.future = data.get("futureOpportunities")
        opp.max_applicants = data.get("maxApplicants")

        db.session.commit()

        return jsonify({"success": True})