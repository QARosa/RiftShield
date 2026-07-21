import React, { Component, type ErrorInfo, type ReactNode } from "react";
import { Box, Button, Heading, Text, VStack } from "@chakra-ui/react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Uncaught UI error:", error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box minH="100vh" display="flex" alignItems="center" justifyContent="center" p={8}>
          <VStack spacing={4} textAlign="center">
            <Heading size="md">Algo deu errado</Heading>
            <Text color="gray.500">Recarregue a página ou tente novamente em instantes.</Text>
            <Button colorScheme="orange" onClick={() => window.location.reload()}>
              Recarregar
            </Button>
          </VStack>
        </Box>
      );
    }

    return this.props.children;
  }
}
