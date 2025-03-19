import React from 'react';
import { ChakraProvider } from "@chakra-ui/react";
import { useState, useEffect } from "react";
import { ModeratorPanel } from "./components/ModeratorPanel";

export function App() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const handleMessage = (event) => {
      console.log("Received message:", event.data);
      if (event.data.type === "OPEN_MODERATOR_PANEL") {
        console.log("Opening modal");
        setIsModalOpen(true);
      }
    };

    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, []);

  console.log("Modal state:", isModalOpen);

  return (
    <ChakraProvider>
      <ModeratorPanel 
        isOpen={isModalOpen} 
        onClose={() => {
          console.log("Closing modal");
          setIsModalOpen(false);
        }} 
      />
    </ChakraProvider>
  );
} 