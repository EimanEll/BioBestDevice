from flask import Flask, render_template, request, redirect, url_for
from database import init_app, db
from models import Vendor, Model, Criteria, Session, UserInput, Weight, ModelScore, Recommendation
import re

app = Flask(__name__)
init_app(app)

# Utility functions for scoring

def parse_numeric_from_string(s):
    # extract first float found
    match = re.search(r"(\d+\.?\d*)", s)
    return float(match.group(1)) if match else None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Create new session
        session = Session()
        db.session.add(session)
        db.session.commit()
        session_id = session.id
        # Fetch criteria
        criteria_list = Criteria.query.all()
        total_weight = 0.0
        weights = {}
        for crit in criteria_list:
            weight_val = request.form.get(f'weight_{crit.id}', type=float)
            if weight_val is None:
                weight_val = 1.0
            weights[crit.id] = weight_val
            total_weight += weight_val
        # Normalize weights
        for crit_id, w in weights.items():
            normalized = w / total_weight if total_weight > 0 else 1.0/len(weights)
            wt = Weight(session_id=session_id, criteria_id=crit_id, weight=normalized)
            db.session.add(wt)
        db.session.commit()
        # Store inputs
        inputs = {}
        for crit in criteria_list:
            val = request.form.get(f'input_{crit.id}')
            if val is not None:
                ui = UserInput(session_id=session_id, criteria_id=crit.id, value=val)
                db.session.add(ui)
                inputs[crit.id] = val
        db.session.commit()
        # Calculate scores
        models = Model.query.all()
        for m in models:
            score = 0.0
            # Budget criterion
            # Expect user enters numeric budget in same currency as cost_estimate
            budget_val = inputs.get_by_key := inputs.get(next((c.id for c in criteria_list if c.name.lower() == 'budget'), None))
            # More robust: find by criteria name
            budget_val = None
            for crit in criteria_list:
                if crit.name.lower() == 'budget':
                    budget_val = inputs.get(crit.id)
                    break
            if budget_val:
                try:
                    budget = float(budget_val)
                    cost = m.cost_estimate or float('inf')
                    if cost <= budget:
                        s = 1.0
                    else:
                        s = budget / cost
                    score += s * next((w.weight for w in Weight.query.filter_by(session_id=session_id, criteria_id=crit.id)), 0)
                except:
                    pass
            # Field Strength
            field_pref = None
            for crit in criteria_list:
                if crit.name.lower() == 'field strength':
                    field_pref = inputs.get(crit.id)
                    field_crit_id = crit.id
                    break
            if field_pref:
                try:
                    pref = float(field_pref)
                    diff = abs((m.field_strength or pref) - pref)
                    # assume max diff 1.0 for normalization
                    s = max(0.0, 1 - diff / 1.0)
                    weight = next((w.weight for w in Weight.query.filter_by(session_id=session_id, criteria_id=field_crit_id)), 0)
                    score += s * weight
                except:
                    pass
            # Patient Comfort (bore type)
            bore_pref = None
            for crit in criteria_list:
                if crit.name.lower() == 'patient comfort':
                    bore_pref = inputs.get(crit.id)
                    bore_crit_id = crit.id
                    break
            if bore_pref:
                s = 1.0 if (m.bore_type and m.bore_type.lower() == bore_pref.lower()) else 0.0
                weight = next((w.weight for w in Weight.query.filter_by(session_id=session_id, criteria_id=bore_crit_id)), 0)
                score += s * weight
            # Maintenance (years)
            maint_pref = None
            for crit in criteria_list:
                if crit.name.lower() == 'maintenance':
                    maint_pref = inputs.get(crit.id)
                    maint_crit_id = crit.id
                    break
            if maint_pref:
                try:
                    years_pref = float(maint_pref)
                    # parse years in service_contract, expecting e.g. "5-year"
                    match = re.search(r"(\d+)", m.service_contract or "")
                    years = float(match.group(1)) if match else 0
                    s = min(years / years_pref, 1.0) if years_pref > 0 else 0.0
                    weight = next((w.weight for w in Weight.query.filter_by(session_id=session_id, criteria_id=maint_crit_id)), 0)
                    score += s * weight
                except:
                    pass
            # Energy Efficiency
            energy_pref = None
            for crit in criteria_list:
                if crit.name.lower() == 'energy efficiency':
                    energy_pref = inputs.get(crit.id)
                    energy_crit_id = crit.id
                    break
            if energy_pref:
                try:
                    max_energy = float(energy_pref)
                    cons = m.energy_consumption or float('inf')
                    s = 1.0 if cons <= max_energy else max_energy / cons
                    weight = next((w.weight for w in Weight.query.filter_by(session_id=session_id, criteria_id=energy_crit_id)), 0)
                    score += s * weight
                except:
                    pass
            # Footprint
            footprint_pref = None
            for crit in criteria_list:
                if crit.name.lower() == 'footprint':
                    footprint_pref = inputs.get(crit.id)
                    footprint_crit_id = crit.id
                    break
            if footprint_pref:
                try:
                    max_space = float(footprint_pref)
                    # parse numeric from model.footprint
                    space = parse_numeric_from_string(m.footprint or "0")
                    s = 1.0 if space <= max_space else max_space / space
                    weight = next((w.weight for w in Weight.query.filter_by(session_id=session_id, criteria_id=footprint_crit_id)), 0)
                    score += s * weight
                except:
                    pass
            # Special Applications
            spec_pref = None
            for crit in criteria_list:
                if crit.name.lower() == 'special applications':
                    spec_pref = inputs.get(crit.id)
                    spec_crit_id = crit.id
                    break
            if spec_pref:
                # expect comma-separated keywords
                prefs = [p.strip().lower() for p in spec_pref.split(',')]
                # look in additional_info and software_features
                text = ((m.additional_info or '') + ' ' + (m.software_features or '')).lower()
                # score: fraction of prefs matched
                if prefs:
                    matches = sum(1 for p in prefs if p in text)
                    s = matches / len(prefs)
                else:
                    s = 0
                weight = next((w.weight for w in Weight.query.filter_by(session_id=session_id, criteria_id=spec_crit_id)), 0)
                score += s * weight
            # Persist score
            ms = ModelScore(session_id=session_id, model_id=m.id, score=score)
            db.session.add(ms)
        db.session.commit()
        # Determine best
        best = ModelScore.query.filter_by(session_id=session_id).order_by(ModelScore.score.desc()).first()
        rationale = ''
        if best:
            m = best.model
            rationale = f"Le modèle sélectionné est {m.name} de {m.vendor.name}. Principaux atouts: champ {m.field_strength}T, bore '{m.bore_type}' pour confort, coût estimé {m.cost_estimate}, contrat '{m.service_contract}', consommation {m.energy_consumption}, adapté aux besoins spécifiés."
            rec = Recommendation(session_id=session_id, model_id=m.id, rationale=rationale)
            db.session.add(rec)
            db.session.commit()
        return redirect(url_for('results', session_id=session_id))
    else:
        # GET: display form
        criteria_list = Criteria.query.all()
        # For fields needing options
        # Field Strength options: extract distinct from models
        strengths = sorted({m.field_strength for m in Model.query.all() if m.field_strength})
        bore_types = sorted({m.bore_type for m in Model.query.all() if m.bore_type})
        return render_template('index.html', criteria_list=criteria_list, strengths=strengths, bore_types=bore_types)

@app.route('/results/<int:session_id>')
def results(session_id):
    session = Session.query.get_or_404(session_id)
    scores = ModelScore.query.filter_by(session_id=session_id).order_by(ModelScore.score.desc()).all()
    recommendation = session.recommendation
    return render_template('results.html', scores=scores, recommendation=recommendation)

@app.route('/detail/<int:model_id>')
def detail(model_id):
    m = Model.query.get_or_404(model_id)
    return render_template('detail.html', model=m)

if __name__ == '__main__':
    app.run(debug=True)