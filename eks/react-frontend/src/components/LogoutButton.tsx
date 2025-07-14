import React from "react";  // needed for React-specific components - like React.FC

interface LogoutButtonProps {
    onLogout: () => void;
}

// FC - Function Component - a type for functional components in React
// React.FC<LogoutButtonProps> - component must receive props of type LogoutButtonProps
const LogoutButton: React.FC<LogoutButtonProps> = ({
    onLogout
}) => (
    <button onClick={onLogout}>Logout</button>
);

// When another file imports from this file, it will get the LoginForm component by default
// not necessary but makes importing cleaner
export default LogoutButton;
