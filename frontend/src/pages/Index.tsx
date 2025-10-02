import { useState } from "react";
import MainPage from "@/components/MainPage";
import Chatbot from "@/components/Chatbot";
import ContractUpload from "@/components/ContractUpload";

type Page = 'main' | 'chatbot' | 'upload';

const Index = () => {
  const [currentPage, setCurrentPage] = useState<Page>('main');

  const handleNavigate = (page: Page) => {
    setCurrentPage(page);
  };

  const handleBack = () => {
    setCurrentPage('main');
  };

  switch (currentPage) {
    case 'chatbot':
      return <Chatbot onBack={handleBack} />;
    case 'upload':
      return <ContractUpload onBack={handleBack} />;
    default:
      return <MainPage onNavigate={handleNavigate} />;
  }
};

export default Index;
