import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import axios from "axios";  // used for making HTTP requests
import LoginForm from "./components/LoginForm"; // import the LoginForm component
import LogoutButton from './components/LogoutButton';
import FetchApp1Root from './components/FetchApp1Root';
import FetchApp2Root from './components/FetchApp2Root';
import FetchApp2FromApp1 from './components/FetchApp2FromApp1';

const AUTH_SERVICE_URL = import.meta.env.VITE_AUTH_SERVICE_URL;
const APP1_URL = import.meta.env.VITE_APP1_URL;
const APP2_URL = import.meta.env.VITE_APP2_URL;

function App() {
  // using `state` - allows remember values between renders and react to user input/changes
  // `username` is state variable, `setUsername` is a function to update it
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginMsg, setLoginMsg] = useState('');
  const [App1RootMsg, setApp1RootMsg] = useState('');
  const [App2RootMsg, setApp2RootMsg] = useState('');
  const [App1ReadApp2Msg, setApp1ReadApp2Msg] = useState('');

  // Track login state
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const fetchApp1Root = async () => {
    try {
      const res = await axios.get(`${APP1_URL}/`, { withCredentials: true });
      setApp1RootMsg(JSON.stringify(res.data));
    } catch (err) {
      setApp1RootMsg("Error fetching app1/");
    }
  };

  const fetchApp2FromApp1 = async () => {
    try {
      const res = await axios.get(`${APP1_URL}/read_app2`, { withCredentials: true });
      setApp1ReadApp2Msg(JSON.stringify(res.data));
    } catch (err) {
      setApp1ReadApp2Msg("Error fetching app1/read_app2");
    }
  };

  const fetchApp2Root = async () => {
    try {
      const res = await axios.get(`${APP2_URL}/`, { withCredentials: true });
      setApp2RootMsg(JSON.stringify(res.data));
    } catch (err) {
      setApp2RootMsg("Error fetching app2/");
    }
  };

  // Update login state on login/logout
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(
        `${AUTH_SERVICE_URL}/login`,
        { username, password },
        { withCredentials: true }
      );
      setLoginMsg("Login successful!");
      setUsername("");
      setPassword("");
      setApp1RootMsg("");
      setApp1ReadApp2Msg("");
      setApp2RootMsg("");
      setIsLoggedIn(true);
    } catch (err) {
      setLoginMsg("Login failed!");
      setUsername("");
      setPassword("");
      setIsLoggedIn(false);
    }
  };

  // Logout function
  const handleLogout = async () => {
    try {
      await axios.post(
        `${AUTH_SERVICE_URL}/logout`,
        {},
        { withCredentials: true }
      );
      setLoginMsg("Logged out.");
      setApp1RootMsg("");
      setApp1ReadApp2Msg("");
      setApp2RootMsg("");
      setIsLoggedIn(false);
    } catch (err) {
      setLoginMsg("Logout failed!");
    }
  };

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem', justifyContent: isLoggedIn ? 'center' : 'flex-start' }}>
        {!isLoggedIn && (
          // <form
          //   style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          //   onSubmit={handleLogin}
          // >
          //   <input
          //     placeholder="username"
          //     value={username}
          //     onChange={e => setUsername(e.target.value)}
          //   />
          //   <input
          //     placeholder="password"
          //     type="password"
          //     value={password}
          //     onChange={e => setPassword(e.target.value)}
          //   />
          //   <button type="submit">Login</button>
          // </form>
          <LoginForm
            username={username}
            password={password}
            setUsername={setUsername}
            setPassword={setPassword}
            onLogin={handleLogin}
          />
        )}
        {isLoggedIn && (
          // <button onClick={handleLogout}>Logout</button>
          <LogoutButton onLogout={handleLogout} />
        )}
      </div>
      <div>{loginMsg}</div>

      <hr />
      <FetchApp1Root
        onFetch={fetchApp1Root}
        result={App1RootMsg}
      />

      <hr />
      <FetchApp2FromApp1
        onFetch={fetchApp2FromApp1}
        result={App1ReadApp2Msg}
      />

      <hr />
      <FetchApp2Root
        onFetch={fetchApp2Root}
        result={App2RootMsg}
      />

    </>
  )
}

export default App
