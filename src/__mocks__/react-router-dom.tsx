import React from 'react';

// Mock React Router DOM for testing
export const BrowserRouter = ({ children }: { children: React.ReactNode }) => (
  <div data-testid="mock-browser-router">{children}</div>
);

export const Routes = ({ children }: { children: React.ReactNode }) => (
  <div data-testid="mock-routes">{children}</div>
);

export const Route = ({ children }: { children?: React.ReactNode }) => (
  <div data-testid="mock-route">{children}</div>
);

export const Navigate = () => <div data-testid="mock-navigate" />;

export const useNavigate = () => jest.fn();

export const useLocation = () => ({
  pathname: '/',
  search: '',
  hash: '',
  state: null,
  key: 'default'
});

export const useParams = () => ({});

export const Link = ({ children, to, ...props }: any) => (
  <a href={to} {...props} data-testid="mock-link">
    {children}
  </a>
);

export const NavLink = ({ children, to, ...props }: any) => (
  <a href={to} {...props} data-testid="mock-navlink">
    {children}
  </a>
);