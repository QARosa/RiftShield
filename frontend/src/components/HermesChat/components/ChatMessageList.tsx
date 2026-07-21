import React from "react";
import { Flex, Box, Text, Menu, MenuButton, MenuList, MenuItem, IconButton, Spinner } from "@chakra-ui/react";
import { MoreVertical, Trash2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import rehypeSanitize from "rehype-sanitize";
import { type ChatMessageListProps } from "../types";
import { useT } from "../../../hooks/useT";
import { useHermesThemeFx } from "../styles/theme-fx";

export const ChatMessageList: React.FC<ChatMessageListProps> = ({
  messages, isLoading, messagesEndRef, onSoftDelete,
}) => {
  const themeFx = useHermesThemeFx();
  const t = useT();
  return (
    <Flex
      flex={1}
      direction="column"
      p={4}
      overflowY="auto"
      css={{
        "&::-webkit-scrollbar": { width: "4px" },
        "&::-webkit-scrollbar-thumb": { background: themeFx.borderColor, borderRadius: "4px" },
      }}
    >
      {messages.map((msg) => (
        <Flex key={msg.id} justify={msg.role === "user" ? "flex-end" : "flex-start"} mb={4}>
          <Flex
            maxW="85%"
            bg={msg.role === "user" ? themeFx.userMsgBg : themeFx.agentMsgBg}
            color={msg.role === "user" ? themeFx.userMsgText : themeFx.agentMsgText}
            p={3}
            borderRadius="xl"
            borderTopRightRadius={msg.role === "user" ? "sm" : "xl"}
            borderTopLeftRadius={msg.role === "agent" ? "sm" : "xl"}
            boxShadow="sm"
            border={msg.role === "agent" ? "1px solid" : "none"}
            borderColor={themeFx.borderColor}
            position="relative"
            role="group"
          >
            <Box
              fontSize="sm"
              sx={{
                p: { marginBottom: "0.5em" },
                "p:last-child": { marginBottom: 0 },
                strong: { fontWeight: "bold", color: msg.role === "user" ? "white" : themeFx.iconColor },
                "ul, ol": { paddingLeft: "1.5em", marginBottom: "0.5em" },
                li: { marginBottom: "0.2em" },
                "h1, h2, h3": { fontWeight: "bold", mt: "1em", mb: "0.5em" },
                "pre, code": { bg: "blackAlpha.300", p: 1, borderRadius: "md", fontSize: "xs" },
              }}
            >
              <ReactMarkdown rehypePlugins={[rehypeSanitize]}>{msg.content}</ReactMarkdown>
            </Box>
            {msg.has_attachment && (
              <Text fontSize="xs" mt={2} fontStyle="italic" color={themeFx.mutedText}>
                📎 Imagem anexada
              </Text>
            )}
            <Box
              position="absolute"
              top="1"
              right={msg.role === "user" ? "auto" : "-8"}
              left={msg.role === "user" ? "-8" : "auto"}
              opacity={0}
              _groupHover={{ opacity: 1 }}
              transition="opacity 0.2s"
            >
              <Menu>
                <MenuButton
                  as={IconButton}
                  icon={<MoreVertical size={14} />}
                  size="xs"
                  variant="ghost"
                  aria-label="Opções"
                  color={themeFx.mutedText}
                />
                <MenuList minW="100px" bg={themeFx.containerBg} borderColor={themeFx.borderColor}>
                  <MenuItem
                    icon={<Trash2 size={14} />}
                    color="red.400"
                    bg="transparent"
                    _hover={{ bg: "whiteAlpha.100" }}
                    onClick={() => onSoftDelete(msg.id)}
                  >
                    Ocultar
                  </MenuItem>
                </MenuList>
              </Menu>
            </Box>
          </Flex>
        </Flex>
      ))}
      {isLoading && (
        <Flex justify="flex-start" mb={4}>
          <Flex
            bg={themeFx.agentMsgBg}
            p={3}
            borderRadius="xl"
            borderTopLeftRadius="sm"
            boxShadow="sm"
            border="1px solid"
            borderColor={themeFx.borderColor}
            align="center"
          >
            <Spinner size="sm" color={themeFx.iconColor} mr={3} />
            <Text fontSize="sm" color={themeFx.mutedText}>{t("hermes.digitando")}</Text>
          </Flex>
        </Flex>
      )}
      <div ref={messagesEndRef} />
    </Flex>
  );
};
