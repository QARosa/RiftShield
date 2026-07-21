import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import {
  ChakraProvider,
  ColorModeScript,
} from "@chakra-ui/react";
import theme from "./theme";
import "./styles/scrollbar.css";
import App from "./components/App";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { ToastProvider } from "./components/Toast/components/ToastContext";

window.addEventListener("unhandledrejection", (event) => {
  console.error("Unhandled promise rejection:", event.reason);
});

window.addEventListener("error", (event) => {
  console.error("Uncaught error:", event.error ?? event.message);
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ColorModeScript initialColorMode={theme.config.initialColorMode} />
    <ChakraProvider theme={theme}>
      <ErrorBoundary>
        <ToastProvider>
          <App />
        </ToastProvider>
      </ErrorBoundary>
    </ChakraProvider>
  </StrictMode>,
);
