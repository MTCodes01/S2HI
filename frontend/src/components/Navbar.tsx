import { useState } from 'react';
import '../styles/global.css';
import { Link, useLocation } from 'react-router-dom';

export default function Navbar() {
    const location = useLocation();
    const [isOpen, setIsOpen] = useState(false);

    const toggleMenu = () => setIsOpen(!isOpen);
    const closeMenu = () => setIsOpen(false);

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <Link to="/" className="navbar-brand" onClick={closeMenu}>
                    <span className="navbar-brand-icon">🧠</span>
                    LEAP
                </Link>

                <button
                    className={`navbar-toggle ${isOpen ? 'active' : ''}`}
                    onClick={toggleMenu}
                    aria-label="Toggle navigation"
                >
                    <span className="bar"></span>
                    <span className="bar"></span>
                    <span className="bar"></span>
                </button>

                <div className={`navbar-links ${isOpen ? 'active' : ''}`}>
                    <Link
                        to="/"
                        className={`navbar-link ${location.pathname === '/' ? 'active' : ''}`}
                        onClick={closeMenu}
                    >
                        Assessment
                    </Link>
                    <Link
                        to="/dashboard"
                        className={`navbar-link ${location.pathname === '/dashboard' ? 'active' : ''}`}
                        onClick={closeMenu}
                    >
                        Dashboard
                    </Link>
                </div>
            </div>
        </nav>
    );
}
