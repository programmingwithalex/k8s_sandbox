import React from "react";  // needed for React-specific components - like React.FC

interface LoginFormProps {
    username: string;
    password: string;
    setUsername: (val: string) => void;
    setPassword: (val: string) => void;
    onLogin: (e: React.FormEvent) => void;
}

// FC - Function Component - a type for functional components in React
// React.FC<LoginFormProps> - component must receive props of type LoginFormProp
const LoginForm: React.FC<LoginFormProps> = ({
    username,
    password,
    setUsername,
    setPassword,
    onLogin,
}) => (
    <form onSubmit={onLogin} className="login-form">
        <input
            type="text"
            placeholder="username"
            value={username}
            // e is the event object
            // e.target.value is the value of the input field
            // setUsername will update the username state - the link is defined in the parent component
            //   - common approach is linking state in parent component to allow parent to use variable in multiple places
            onChange={e => setUsername(e.target.value)}
        />
        <input
            type="password"
            placeholder="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
        />
        <button type="submit">Login</button>
    </form>
);

// When another file imports from this file, it will get the LoginForm component by default
// not necessary but makes importing cleaner
export default LoginForm;