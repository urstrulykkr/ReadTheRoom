import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Button,
  Input,
  Tabs,
  TabList,
  Tab,
  Box,
  Text,
  Badge,
  Flex,
  Stack,
  ButtonGroup,
} from "@chakra-ui/react";

export const ModeratorPanel = ({ isOpen, onClose }) => {
  console.log("ModeratorPanel render - isOpen:", isOpen);
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md">
      <ModalOverlay />
      <ModalContent
        position="fixed"
        right={0}
        top={0}
        height="100vh"
        width="400px"
        borderRadius="0"
        m={0}
      >
        <ModalHeader borderBottomWidth="1px">Read the Room</ModalHeader>
        <ModalCloseButton />
        
        <ModalBody p={4}>
          <Stack spacing={4}>
            {/* Search Bar */}
            <Input
              placeholder="Search for past questions/comments"
              size="md"
              borderRadius="full"
            />

            {/* Tabs */}
            <Tabs>
              <TabList>
                <Tab>Queue</Tab>
                <Tab>Flagged</Tab>
                <Tab>Archive</Tab>
              </TabList>
            </Tabs>

            {/* AI Summary */}
            <Box bg="gray.50" p={4} borderRadius="lg">
              <Text fontWeight="bold">AI Summary</Text>
              <Flex align="center" mt={2}>
                <Badge colorScheme="yellow" borderRadius="full" px={3}>
                  Publicizing
                </Badge>
                <Text color="green.500" fontWeight="bold" ml={2}>
                  Very High
                </Text>
              </Flex>
              <Text fontSize="sm" color="gray.600" mt={2}>
                This post possibly contains attempts to publicize a legal problem...
              </Text>
            </Box>

            {/* Post Content */}
            <Box borderWidth="1px" p={4} borderRadius="lg">
              <Flex align="center">
                <Text fontWeight="bold">u/sam040501</Text>
                <Text fontSize="sm" color="gray.500" ml={2}>
                  • Post • Today, 12:32 PM
                </Text>
              </Flex>
              <Text mt={2} fontWeight="medium">
                Facing Legal Trouble with Airbnb in Barcelona, What Should I Do?
              </Text>
              <Text fontSize="sm" color="gray.600" mt={2}>
                I've recently been fined by local authorities in Barcelona for renting out my apartment on Airbnb, which is apparently against new regulations...
              </Text>
            </Box>

            {/* Moderation Actions */}
            <ButtonGroup spacing={2} width="100%">
              <Button
                colorScheme="red"
                borderRadius="full"
                flex={1}
              >
                Remove
              </Button>
              <Button
                colorScheme="blue"
                borderRadius="full"
                flex={1}
              >
                Keep
              </Button>
              <Button
                colorScheme="blackAlpha"
                borderRadius="full"
                flex={1}
              >
                Ban User
              </Button>
              <Button
                colorScheme="gray"
                borderRadius="full"
                flex={1}
              >
                Send Modmail
              </Button>
            </ButtonGroup>
          </Stack>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
}; 