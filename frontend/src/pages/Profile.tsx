import useUser from "../context/UserContext";
export default function Profile() {
    const { user } = useUser();
    return (
        <div className="profile-page" style={{ padding: '2rem' }}>
            <h1>Profile Information</h1>
            <p><strong>Username:</strong> {user?.username}</p>
            <p><strong>Email:</strong> {user?.email}</p>
            <p><strong>Password:</strong> {user?.password}</p>
            <p><strong>First Name:</strong> {user?.firstName}</p>
            <p><strong>Last Name:</strong> {user?.lastName}</p>
            <p><strong>Birthday:</strong> {user?.birthday}</p>
            <p><strong>Age:</strong> {user?.age}</p>
            <p><strong>Husky ID:</strong> {user?.studentId}</p>
            <p><strong>Phone:</strong> {user?.phoneNo}</p>
            <p><strong>Gender:</strong> {user?.gender}</p>
            <p><strong>Years Experience:</strong> {user?.yearsExperience}</p>
            <p><strong>Skill Level:</strong> {user?.skillLevel}</p>
            <p><strong>UTR:</strong> {user?.utrRating ?? '—'}</p>
            <p><strong>Competitive Experience:</strong> {user?.hasPlayedCompetitive === true ? 'Yes' : user?.hasPlayedCompetitive === false ? 'No' : '—'}</p>
            <p><strong>Tennis Rating:</strong> {user?.rating ?? '—'}</p>
        </div>
    )
}