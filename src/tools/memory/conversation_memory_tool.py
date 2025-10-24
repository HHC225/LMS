"""
Conversation Memory Tool Implementation
ChromaDB-based conversation memory management for storing and retrieving important conversation context
"""
from typing import Dict, Any, List, Optional
from fastmcp import Context
from datetime import datetime
import chromadb
from chromadb.config import Settings
import json
import os
from pathlib import Path
from ..base import ReasoningTool


class ConversationMemoryTool(ReasoningTool):
    """Conversation Memory Tool for managing conversation context with ChromaDB"""
    
    def __init__(self, persist_directory: str = "./output/chroma_db"):
        super().__init__(
            name="conversation_memory",
            description="ChromaDB-based conversation memory management tool"
        )
        
        # Initialize ChromaDB client with persistence
        self.persist_directory = os.path.abspath(persist_directory)
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client with proper settings
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
                is_persistent=True
            )
        )
        
        # Get or create collection for conversation memories
        # Use try-except to handle potential collection issues
        try:
            self.collection = self.client.get_or_create_collection(
                name="conversation_memories",
                metadata={"description": "Stores important conversation summaries"}
            )
        except Exception as e:
            # If there's an error, try to reset and recreate
            print(f"Warning: Error initializing collection, resetting: {e}")
            try:
                self.client.reset()
            except:
                pass
            self.collection = self.client.get_or_create_collection(
                name="conversation_memories",
                metadata={"description": "Stores important conversation summaries"}
            )
    
    async def execute(
        self,
        action: str,
        ctx: Optional[Context] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute conversation memory action
        
        Args:
            action: Action to perform (store, query, list, delete, clear, update, get)
            ctx: FastMCP context
            **kwargs: Action-specific parameters
        
        Returns:
            Dict containing action results
        """
        await self.log_execution(ctx, f"Executing conversation memory action: {action}")
        
        if action == "store":
            return await self._store_conversation(ctx, **kwargs)
        elif action == "query":
            return await self._query_conversations(ctx, **kwargs)
        elif action == "list":
            return await self._list_conversations(ctx, **kwargs)
        elif action == "delete":
            return await self._delete_conversation(ctx, **kwargs)
        elif action == "clear":
            return await self._clear_all(ctx)
        elif action == "update":
            return await self._update_conversation(ctx, **kwargs)
        elif action == "get":
            return await self._get_conversation(ctx, **kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _store_conversation(
        self,
        ctx: Optional[Context],
        conversation_text: str,
        speaker: Optional[str] = None,
        summary: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Store conversation in vector database
        
        Args:
            ctx: FastMCP context
            conversation_text: The conversation content to store (always stores full text)
            speaker: Name of the speaker (optional)
            summary: Summary of the conversation (optional, stored in metadata for reference only)
            metadata: Additional metadata to store
            conversation_id: Unique identifier for this conversation (auto-generated if None)
        
        Returns:
            Dict with storage confirmation and ID
        """
        try:
            # Ensure collection is available
            try:
                self.collection = self.client.get_or_create_collection(
                    name="conversation_memories",
                    metadata={"description": "Stores important conversation summaries"}
                )
            except Exception as coll_err:
                await self.log_execution(ctx, f"Error accessing collection, reinitializing: {coll_err}")
                # Reinitialize client and collection
                self.client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True,
                        is_persistent=True
                    )
                )
                self.collection = self.client.get_or_create_collection(
                    name="conversation_memories",
                    metadata={"description": "Stores important conversation summaries"}
                )
            
            # Generate ID if not provided
            if not conversation_id:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                conversation_id = f"conv_{timestamp}"
            
            # Always store full conversation text to prevent information loss
            document = conversation_text
            
            # Prepare metadata
            meta = {
                "timestamp": datetime.now().isoformat(),
                "character_count": len(conversation_text)
            }
            
            if speaker:
                meta["speaker"] = speaker
            
            # Store summary in metadata if provided (for reference only)
            if summary:
                meta["summary"] = summary
                meta["has_summary"] = True
            
            if metadata:
                # Convert metadata values to ChromaDB-compatible types
                # ChromaDB only accepts: str, int, float, bool, or None
                sanitized_metadata = {}
                for key, value in metadata.items():
                    if isinstance(value, (list, tuple)):
                        # Convert lists/tuples to comma-separated strings
                        sanitized_metadata[key] = ", ".join(str(v) for v in value)
                    elif isinstance(value, dict):
                        # Convert dicts to JSON strings
                        sanitized_metadata[key] = json.dumps(value)
                    elif isinstance(value, (str, int, float, bool)) or value is None:
                        # Keep primitive types as-is
                        sanitized_metadata[key] = value
                    else:
                        # Convert other types to strings
                        sanitized_metadata[key] = str(value)
                
                meta.update(sanitized_metadata)
            
            # Store in ChromaDB with automatic embedding
            self.collection.add(
                documents=[document],
                metadatas=[meta],
                ids=[conversation_id]
            )
            
            await self.log_execution(
                ctx,
                f"Stored conversation with ID: {conversation_id}"
            )
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "message": "Conversation stored successfully",
                "metadata": meta,
                "document_length": len(document)
            }
            
        except Exception as e:
            error_msg = f"Error storing conversation: {str(e)}"
            await self.log_execution(ctx, error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def _query_conversations(
        self,
        ctx: Optional[Context],
        query_text: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query conversations using semantic search
        
        Args:
            ctx: FastMCP context
            query_text: Text to search for
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            Dict with query results
        """
        try:
            # Ensure collection is available
            try:
                self.collection = self.client.get_or_create_collection(
                    name="conversation_memories",
                    metadata={"description": "Stores important conversation summaries"}
                )
            except Exception as coll_err:
                await self.log_execution(ctx, f"Error accessing collection, reinitializing: {coll_err}")
                # Reinitialize client and collection
                self.client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True,
                        is_persistent=True
                    )
                )
                self.collection = self.client.get_or_create_collection(
                    name="conversation_memories",
                    metadata={"description": "Stores important conversation summaries"}
                )
            
            # Query ChromaDB with automatic embedding
            query_params = {
                "query_texts": [query_text],
                "n_results": n_results
            }
            
            if filter_metadata:
                query_params["where"] = filter_metadata
            
            results = self.collection.query(**query_params)
            
            # Format results
            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    result_item = {
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results else None
                    }
                    formatted_results.append(result_item)
            
            await self.log_execution(
                ctx,
                f"Query returned {len(formatted_results)} results"
            )
            
            return {
                "success": True,
                "query": query_text,
                "results": formatted_results,
                "count": len(formatted_results)
            }
            
        except Exception as e:
            error_msg = f"Error querying conversations: {str(e)}"
            await self.log_execution(ctx, error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def _list_conversations(
        self,
        ctx: Optional[Context],
        limit: Optional[int] = None,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List all stored conversations
        
        Args:
            ctx: FastMCP context
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip
        
        Returns:
            Dict with list of conversations
        """
        try:
            # Ensure collection is available
            try:
                self.collection = self.client.get_or_create_collection(
                    name="conversation_memories",
                    metadata={"description": "Stores important conversation summaries"}
                )
            except Exception as coll_err:
                await self.log_execution(ctx, f"Error accessing collection, reinitializing: {coll_err}")
                self.client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True,
                        is_persistent=True
                    )
                )
                self.collection = self.client.get_or_create_collection(
                    name="conversation_memories",
                    metadata={"description": "Stores important conversation summaries"}
                )
            
            # Get all items from collection
            results = self.collection.get(
                limit=limit,
                offset=offset,
                include=["documents", "metadatas"]
            )
            
            # Format results
            conversations = []
            if results["ids"]:
                for i in range(len(results["ids"])):
                    conv = {
                        "id": results["ids"][i],
                        "document": results["documents"][i] if results["documents"] else None,
                        "metadata": results["metadatas"][i] if results["metadatas"] else None
                    }
                    conversations.append(conv)
            
            await self.log_execution(
                ctx,
                f"Listed {len(conversations)} conversations"
            )
            
            return {
                "success": True,
                "conversations": conversations,
                "count": len(conversations),
                "total_in_db": self.collection.count()
            }
            
        except Exception as e:
            error_msg = f"Error listing conversations: {str(e)}"
            await self.log_execution(ctx, error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def _delete_conversation(
        self,
        ctx: Optional[Context],
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Delete a specific conversation
        
        Args:
            ctx: FastMCP context
            conversation_id: ID of conversation to delete
        
        Returns:
            Dict with deletion confirmation
        """
        try:
            # Ensure collection is available
            try:
                self.collection = self.client.get_or_create_collection(
                    name="conversation_memories",
                    metadata={"description": "Stores important conversation summaries"}
                )
            except Exception as coll_err:
                await self.log_execution(ctx, f"Error accessing collection, reinitializing: {coll_err}")
                self.client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True,
                        is_persistent=True
                    )
                )
                self.collection = self.client.get_or_create_collection(
                    name="conversation_memories",
                    metadata={"description": "Stores important conversation summaries"}
                )
            
            self.collection.delete(ids=[conversation_id])
            
            await self.log_execution(
                ctx,
                f"Deleted conversation: {conversation_id}"
            )
            
            return {
                "success": True,
                "message": f"Conversation {conversation_id} deleted successfully"
            }
            
        except Exception as e:
            error_msg = f"Error deleting conversation: {str(e)}"
            await self.log_execution(ctx, error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def _get_conversation(
        self,
        ctx: Optional[Context],
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Get a specific conversation by ID
        
        Args:
            ctx: FastMCP context
            conversation_id: ID of conversation to retrieve
        
        Returns:
            Dict with conversation data
        """
        try:
            # Ensure collection is available
            try:
                self.collection = self.client.get_or_create_collection(
                    name="conversation_memories",
                    metadata={"description": "Stores important conversation summaries"}
                )
            except Exception as coll_err:
                await self.log_execution(ctx, f"Error accessing collection, reinitializing: {coll_err}")
                self.client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True,
                        is_persistent=True
                    )
                )
                self.collection = self.client.get_or_create_collection(
                    name="conversation_memories",
                    metadata={"description": "Stores important conversation summaries"}
                )
            
            # Get specific conversation
            results = self.collection.get(
                ids=[conversation_id],
                include=["documents", "metadatas"]
            )
            
            if not results["ids"] or len(results["ids"]) == 0:
                return {
                    "success": False,
                    "error": f"Conversation with ID '{conversation_id}' not found"
                }
            
            conversation = {
                "id": results["ids"][0],
                "document": results["documents"][0] if results["documents"] else None,
                "metadata": results["metadatas"][0] if results["metadatas"] else None
            }
            
            await self.log_execution(
                ctx,
                f"Retrieved conversation: {conversation_id}"
            )
            
            return {
                "success": True,
                "conversation": conversation
            }
            
        except Exception as e:
            error_msg = f"Error retrieving conversation: {str(e)}"
            await self.log_execution(ctx, error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def _update_conversation(
        self,
        ctx: Optional[Context],
        conversation_id: str,
        conversation_text: Optional[str] = None,
        speaker: Optional[str] = None,
        summary: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        merge_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Update an existing conversation
        
        Args:
            ctx: FastMCP context
            conversation_id: ID of conversation to update
            conversation_text: New conversation content (optional, keeps existing if None)
            speaker: New speaker name (optional)
            summary: New summary (optional)
            metadata: New metadata (optional)
            merge_metadata: If True, merge with existing metadata; if False, replace completely
        
        Returns:
            Dict with update confirmation
        """
        try:
            # Ensure collection is available
            try:
                self.collection = self.client.get_or_create_collection(
                    name="conversation_memories",
                    metadata={"description": "Stores important conversation summaries"}
                )
            except Exception as coll_err:
                await self.log_execution(ctx, f"Error accessing collection, reinitializing: {coll_err}")
                self.client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True,
                        is_persistent=True
                    )
                )
                self.collection = self.client.get_or_create_collection(
                    name="conversation_memories",
                    metadata={"description": "Stores important conversation summaries"}
                )
            
            # First, get existing conversation
            existing = self.collection.get(
                ids=[conversation_id],
                include=["documents", "metadatas"]
            )
            
            if not existing["ids"] or len(existing["ids"]) == 0:
                return {
                    "success": False,
                    "error": f"Conversation with ID '{conversation_id}' not found. Use 'store' to create new conversations."
                }
            
            # Get existing data
            existing_document = existing["documents"][0] if existing["documents"] else ""
            existing_metadata = existing["metadatas"][0] if existing["metadatas"] else {}
            
            # Prepare new document (use existing if not provided)
            # Always store full conversation text to prevent information loss
            if conversation_text is not None:
                new_document = conversation_text
            else:
                new_document = existing_document
            
            # Prepare metadata
            if merge_metadata and existing_metadata:
                # Merge with existing metadata
                meta = existing_metadata.copy()
            else:
                # Start fresh
                meta = {}
            
            # Update timestamp
            meta["timestamp"] = datetime.now().isoformat()
            meta["updated"] = True
            
            # Update fields if provided
            if conversation_text is not None:
                meta["character_count"] = len(conversation_text)
            
            if speaker is not None:
                meta["speaker"] = speaker
            
            # Store summary in metadata if provided (for reference only)
            if summary is not None:
                meta["summary"] = summary
                meta["has_summary"] = True
            
            # Add or update custom metadata
            if metadata:
                # Sanitize metadata for ChromaDB
                sanitized_metadata = {}
                for key, value in metadata.items():
                    if isinstance(value, (list, tuple)):
                        sanitized_metadata[key] = ", ".join(str(v) for v in value)
                    elif isinstance(value, dict):
                        sanitized_metadata[key] = json.dumps(value)
                    elif isinstance(value, (str, int, float, bool)) or value is None:
                        sanitized_metadata[key] = value
                    else:
                        sanitized_metadata[key] = str(value)
                
                meta.update(sanitized_metadata)
            
            # Update in ChromaDB using upsert
            self.collection.upsert(
                documents=[new_document],
                metadatas=[meta],
                ids=[conversation_id]
            )
            
            await self.log_execution(
                ctx,
                f"Updated conversation with ID: {conversation_id}"
            )
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "message": "Conversation updated successfully",
                "metadata": meta,
                "document_length": len(new_document),
                "was_merged": merge_metadata
            }
            
        except Exception as e:
            error_msg = f"Error updating conversation: {str(e)}"
            await self.log_execution(ctx, error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    async def _clear_all(
        self,
        ctx: Optional[Context]
    ) -> Dict[str, Any]:
        """
        Clear all conversations from database
        
        Args:
            ctx: FastMCP context
        
        Returns:
            Dict with clear confirmation
        """
        try:
            # Ensure collection is available
            try:
                self.collection = self.client.get_or_create_collection(
                    name="conversation_memories",
                    metadata={"description": "Stores important conversation summaries"}
                )
            except Exception as coll_err:
                await self.log_execution(ctx, f"Error accessing collection, reinitializing: {coll_err}")
                self.client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True,
                        is_persistent=True
                    )
                )
                self.collection = self.client.get_or_create_collection(
                    name="conversation_memories",
                    metadata={"description": "Stores important conversation summaries"}
                )
            
            # Get count before clearing
            count_before = self.collection.count()
            
            # Delete collection and recreate
            self.client.delete_collection(name="conversation_memories")
            self.collection = self.client.get_or_create_collection(
                name="conversation_memories",
                metadata={"description": "Stores important conversation summaries"}
            )
            
            await self.log_execution(
                ctx,
                f"Cleared all conversations ({count_before} items)"
            )
            
            return {
                "success": True,
                "message": f"Cleared all conversations ({count_before} items removed)"
            }
            
        except Exception as e:
            error_msg = f"Error clearing conversations: {str(e)}"
            await self.log_execution(ctx, error_msg)
            return {
                "success": False,
                "error": error_msg
            }
