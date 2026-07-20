import { Flex, Text } from "@chakra-ui/react";
import { useLanguage } from "../context/LanguageContext";
import { BrazilFlagMini, USAFlagMini } from "./LanguageFlags";

export function LanguageToggle() {
  const { lang, setLang } = useLanguage();

  return (
    <Flex
      as="button"
      type="button"
      align="center"
      gap={1.5}
      cursor="pointer"
      onClick={() => setLang(lang === "pt-BR" ? "en-US" : "pt-BR")}
      aria-label={lang === "pt-BR" ? "Switch to English" : "Mudar para Português"}
      title={lang === "pt-BR" ? "Mudar para inglês" : "Switch to Portuguese"}
      _hover={{ opacity: 0.8, transform: "scale(1.05)" }}
      transition="all 0.2s"
      userSelect="none"
      px={1.5}
      py={1}
      borderRadius="md"
    >
      {lang === "pt-BR" ? <BrazilFlagMini /> : <USAFlagMini />}
      <Text fontSize="xs" fontWeight="bold" lineHeight="1">
        {lang === "pt-BR" ? "PT" : "EN"}
      </Text>
    </Flex>
  );
}
