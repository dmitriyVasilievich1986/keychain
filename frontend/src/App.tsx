import './App.css';
import { Login } from '@pages/login';
import { Routes, Route } from 'react-router';

import { ProtectedRoute } from '@components/protectedRoute';

import { Navbar } from './components/navbar';


function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <p>Hello World</p>
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
}

export default App;
