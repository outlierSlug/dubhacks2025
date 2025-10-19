import React, { useEffect, useState, useMemo } from "react";
import useUser from "../context/UserContext";
import "../styles/Profile.css";
import { TennisRating, type RatingInputs } from "../utils/TennisRating";

export default function Profile() {
    const { user, updateUser, setUser } = useUser() as any;
    const [editing, setEditing] = useState(false);
    const [form, setForm] = useState<any>(null);
    const [status, setStatus] = useState<string | null>(null);
    const [touched, setTouched] = useState<Record<string, boolean>>({});

    const errors = useMemo(() => {
        const errs: Record<string, string> = {};
        if (touched.email && (!form?.email || !form.email.includes('@'))) 
            errs.email = 'Enter a valid email';
        if (touched.firstName && !form?.firstName) 
            errs.firstName = 'First name is required';
        if (touched.lastName && !form?.lastName) 
            errs.lastName = 'Last name is required';
        if (touched.phoneNo && !form?.phoneNo) 
            errs.phoneNo = 'Phone number is required';

        const yearsNum = Number(form?.yearsExperience);
        if (touched.yearsExperience && (isNaN(yearsNum) || yearsNum < 0)) 
            errs.yearsExperience = 'Enter valid years of experience';

        if (touched.skillLevel && !form?.skillLevel) 
            errs.skillLevel = 'Select a relative level';

        if (touched.utrRating && form.utrRating !== '') {
            const utr = parseFloat(form.utrRating)
            if (isNaN(utr)) errs.utrRating = 'UTR must be a number'
            else if (utr < 1 || utr > 16.5) errs.utrRating = 'UTR must be between 1.00 and 16.50'
            else {
                // Check if it has more than 2 decimal places
                const scaled = Math.round(utr * 100)
                if (Math.abs(utr * 100 - scaled) > 0.0001) {
                errs.utrRating = 'Use hundredths (e.g., 7.25)'
                }
            }
        }
        return errs;
    }, [form, touched]);

    function computeAgeFromBirthday(birthday?: string | null) {
        if (!birthday) return undefined;
        const bd = new Date(birthday);
        if (Number.isNaN(bd.getTime())) return undefined;
        const today = new Date();
        let age = today.getFullYear() - bd.getFullYear();
        const m = today.getMonth() - bd.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < bd.getDate())) age--;
        return age;
    }

    function computeRatingFromForm(f: any) {
        try {
            const skillMap = { beginner: 1, intermediate: 2, advanced: 3 } as const;
            const skillNumeric = skillMap[f?.skillLevel as keyof typeof skillMap] || 1;
            
            const yearsPlayed = f?.yearsExperience ? Number(f.yearsExperience) : 0;
            const utr = f?.utrRating ? parseFloat(Number(f.utrRating).toFixed(2)) : undefined;
            
            const rating = TennisRating.calculate({
                utr,
                skillLevel: skillNumeric,
                yearsPlayed,
                hasCompExperience: Boolean(f?.hasPlayedCompetitive)
            });

            return rating;
        } catch (error) {
            console.warn('Error computing tennis rating:', error);
            return undefined;
        }
    }

    useEffect(() => {
        if (!user) {
            setForm(null);
            return;
        }
        const init = { ...user };
        const computedAge = computeAgeFromBirthday(init.birthday);
        if (computedAge !== undefined) init.age = computedAge;
        const computedRating = computeRatingFromForm(init);
        if (computedRating !== undefined) init.rating = computedRating;
        setForm(init);
    }, [user]);

    if (!user || !form) {
        return <div className="profile-page">Loading...</div>;
    }

    const editableFields = Object.keys(form).filter(k => 
        k !== "username" && k !== "age" && k !== "rating"
    );

    const displayOrder = [
        "email",
        "firstName",
        "lastName",
        "phoneNo",
        "yearsExperience",
        "skillLevel",
        "utrRating",
        "rating",
        "birthday",
        "studentId",
        "hasPlayedCompetitive"
    ];

    function labelForKey(key: string) {
        if (key === "utrRating") return "UTR Rating";
        if (key === "phoneNo") return "Phone Number";
        if (key === "studentId") return "Husky ID";
        return key.replace(/([A-Z])/g, " $1").replace(/^./, s => s.toUpperCase());
    }

    function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) {
        const { name, value } = e.target;
        setTouched(prev => ({ ...prev, [name]: true }));
        
        const next = { ...form, [name]: value };

        if (name === "birthday" || next.birthday) {
            const computedAge = computeAgeFromBirthday(next.birthday);
            if (computedAge !== undefined) next.age = computedAge;
            else delete next.age;
        }

        if (name === "utrRating" || name === "yearsExperience" || 
            name === "skillLevel" || name === "hasPlayedCompetitive" ||
            next.utrRating || next.yearsExperience) {
            const computedRating = computeRatingFromForm(next);
            if (computedRating !== undefined) next.rating = computedRating;
            else delete next.rating;
        }

        if (name === "hasPlayedCompetitive") {
            next[name] = value === "true";
        }

        setForm(next);
    }

    function handleSave() {
        const allTouched = editableFields.reduce((acc, field) => ({
            ...acc,
            [field]: true
        }), {});
        setTouched(allTouched);

        if (Object.keys(errors).length > 0) {
            setStatus("Please fix the errors before saving.");
            return;
        }

        const final = { ...form };
        const computedAge = computeAgeFromBirthday(final.birthday);
        if (computedAge !== undefined) final.age = computedAge;
        const computedRating = computeRatingFromForm(final);
        if (computedRating !== undefined) final.rating = computedRating;

        if (typeof updateUser === "function") {
            updateUser(final)
                .then?.(() => {
                    setStatus("Saved.");
                    setEditing(false);
                })
                .catch((err: any) => setStatus("Save failed."));
        } else if (typeof setUser === "function") {
            setUser(final);
            setStatus("Saved (local).");
            setEditing(false);
        } else {
            console.warn("No updater in UserContext; changes are local only.");
            setStatus("Changes are local only (no updater provided).");
            setEditing(false);
        }
    }

    function handleCancel() {
        setForm({ ...user });
        const computedAge = computeAgeFromBirthday(user.birthday);
        if (computedAge !== undefined) setForm((s:any)=>({...s, age: computedAge}));
        const computedRating = computeRatingFromForm(user);
        if (computedRating !== undefined) setForm((s:any)=>({...s, rating: computedRating}));
        setEditing(false);
        setStatus(null);
        setTouched({});
    }
    return (
        <div className="profile-page card">
            <div className="profile-header">
                <h1>Profile</h1>
                {!editing ? (
                    <button className="btn btn-primary" onClick={() => setEditing(true)}>Edit</button>
                ) : (
                    <div className="button-group">
                        <button className="btn btn-primary" onClick={handleSave}>Save</button>
                        <button className="btn btn-ghost" onClick={handleCancel}>Cancel</button>
                    </div>
                )}
            </div>

            <div className="profile-grid">
                <div className="profile-row">
                    <label>Username</label>
                    <div className="value">{user.username}</div>
                </div>

                {displayOrder.map((key) => (
                    <React.Fragment key={key}>
                        <div className="profile-row">
                            <label>{labelForKey(key)}</label>
                            <div className="input-container">
                                {editing && editableFields.includes(key) ? (
                                    <>
                                        {key === "hasPlayedCompetitive" ? (
                                            <select
                                                name={key}
                                                value={form[key] === true ? "true" : form[key] === false ? "false" : ""}
                                                onChange={handleChange}
                                                className={`input ${errors[key] ? 'error' : ''}`}
                                            >
                                                <option value="">—</option>
                                                <option value="true">Yes</option>
                                                <option value="false">No</option>
                                            </select>
                                        ) : key === "skillLevel" ? (
                                            <select
                                                name={key}
                                                value={form[key] ?? ""}
                                                onChange={handleChange}
                                                className={`input ${errors[key] ? 'error' : ''}`}
                                            >
                                                <option value="">Select level</option>
                                                <option value="beginner">Beginner</option>
                                                <option value="intermediate">Intermediate</option>
                                                <option value="advanced">Advanced</option>
                                            </select>
                                        ) : (
                                            <input
                                                name={key}
                                                value={form[key] ?? ""}
                                                onChange={handleChange}
                                                className={`input ${errors[key] ? 'error' : ''}`}
                                                type={key === "utrRating" || key === "yearsExperience" ? "number" : 
                                                      key === "birthday" ? "date" : "text"}
                                            />
                                        )}
                                        {errors[key] && (
                                            <div className="error-message">{errors[key]}</div>
                                        )}
                                    </>
                                ) : (
                                    <div className="value">
                                        {key === "hasPlayedCompetitive"
                                            ? (form[key] === true ? "Yes" : form[key] === false ? "No" : "—")
                                            : (form[key] ?? "—")}
                                    </div>
                                )}
                            </div>
                        </div>
                    </React.Fragment>
                ))}

                <div className="profile-row">
                    <label>Age</label>
                    <div className="value">{form.age ?? '—'}</div>
                </div>
            </div>

            {status && <div className="status">{status}</div>}
        </div>
    );
}