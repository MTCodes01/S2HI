import '../styles/global.css';
import { Link, useLocation } from 'react-router-dom';

export default function Navbar() {
    const location = useLocation();

    return (
        <nav className="navbar">
            <Link to="/" className="navbar-brand">
                <span className="navbar-brand-icon">🧠</span>
                S2HI Assessment
            </Link>
            <div className="navbar-links">
                <Link
                    to="/"
                    className={`navbar-link ${location.pathname === '/' ? 'active' : ''}`}
                >
                    Assessment
                </Link>
                <Link
                    to="/dashboard"
                    className={`navbar-link ${location.pathname === '/dashboard' ? 'active' : ''}`}
                >
                    Dashboard
                </Link>
            </div>
        </nav>
    );
}
