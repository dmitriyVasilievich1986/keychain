import './App.css';
import { Login } from '@pages/login';
import { Password } from '@pages/password';
import { Routes, Route, Navigate } from 'react-router';

import { Navbar } from '@components/navbar';
import { ProtectedRoute } from '@components/protectedRoute';

function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Navigate to="/password" replace />} />
        <Route
          path="/password"
          element={
            <ProtectedRoute>
              <Password />
            </ProtectedRoute>
          }
        />
        <Route
          path="/password/:passwordId"
          element={
            <ProtectedRoute>
              <Password />
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
}

export default App;
