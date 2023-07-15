import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import api from '../interceptor/api';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();
    
    // handle send form submit
    const handleSubmit = async (e) => {
      e.preventDefault();
      
      // object form datas
      const formData = {
        username: username,
        password: password
      };
      
      try {
        // post to API to authenticate
        const response = await api.post('/auth-token/', formData);

        if (response.status === 200) {
          localStorage.setItem('token', response.data.token);
          
          // Redirect
          navigate('/home');
        }
      } catch (error) {
        console.log(error);
      }
    };
    
    return (
      <div>
        <h2>Login</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit">Login</button>
        </form>
      </div>
    );
  };
  
  export default Login;
  