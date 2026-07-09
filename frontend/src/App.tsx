import './App.css';
import { CreatePassword } from '@pages/createPassword';
import { Login } from '@pages/login';
import { Logout } from '@pages/logout';
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
        <Route path="/logout" element={<Logout />} />
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
          path="/password/create"
          element={
            <ProtectedRoute>
              <CreatePassword />
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
        <Route path="*" element={<Navigate to="/password" replace />} />
      </Routes>
    </>
  );
}

export default App;
