import './App.css';
import { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router';

import { Navbar } from '@components/navbar';
import { ProtectedRoute } from '@components/protectedRoute';

const Login = lazy(() => import('@pages/login').then((module) => ({ default: module.Login })));
const Password = lazy(() =>
  import('@pages/password').then((module) => ({ default: module.Password }))
);
const CreatePassword = lazy(() =>
  import('@pages/createPassword').then((module) => ({ default: module.CreatePassword }))
);

function App() {
  return (
    <>
      <Navbar />
      <Suspense fallback={null}>
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
      </Suspense>
    </>
  );
}

export default App;
