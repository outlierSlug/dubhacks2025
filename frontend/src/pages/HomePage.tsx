import useUser from "../context/UserContext";
export default function HomePage() {

    const { user } = useUser();
    return (
        <div className="home-page" style={{ padding: '2rem' }}>
            <h1>🎾 Welcome to DubRally! 🎾</h1>
        </div>
    )
}