import { useState, useEffect, useCallback } from 'react';
import { recipeAPI } from '../services/api';

export const useRecipes = () => {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Pagination state
  const [paginationData, setPaginationData] = useState({
    total: 0,
    page: 1,
    pages: 0,
    per_page: 10,
    has_next: false,
    has_prev: false
  });

  const loadRecipes = useCallback(async (page = 1, pageSize = 10) => {
    try {
      setLoading(true);
      setError(null);
      const response = await recipeAPI.getRecipes(page, pageSize);
      
      // response is now a PaginatedResponse object
      setRecipes(response.items);
      setPaginationData({
        total: response.total,
        page: response.page,
        pages: response.pages,
        per_page: response.per_page,
        has_next: response.has_next,
        has_prev: response.has_prev
      });
    } catch (err) {
      setError(err.userMessage || err.message);
      console.error('Error loading recipes:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Search recipes with pagination
  const searchRecipes = useCallback(async (query = '', page = 1, pageSize = 10, filters = {}) => {
    try {
      setLoading(true);
      setError(null);
      const response = await recipeAPI.searchRecipes(query, page, pageSize, filters);
      
      setRecipes(response.items);
      setPaginationData({
        total: response.total,
        page: response.page,
        pages: response.pages,
        per_page: response.per_page,
        has_next: response.has_next,
        has_prev: response.has_prev
      });
    } catch (err) {
      setError(err.userMessage || err.message);
      console.error('Error searching recipes:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load recipes on component mount
  useEffect(() => {
    loadRecipes();
  }, [loadRecipes]);

  const generateRecipes = useCallback(async (requestData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await recipeAPI.generateRecipes(requestData);
      
      // Return the response without automatically saving recipes
      return response;
    } catch (err) {
      setError(err.userMessage || err.message);
      console.error('Error generating recipes:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteRecipe = useCallback(async (recipeId) => {
    try {
      await recipeAPI.deleteRecipe(recipeId);
      
      // Reload current page to get updated results
      loadRecipes(paginationData.page, paginationData.per_page);
    } catch (err) {
      setError(err.userMessage || err.message);
      console.error('Error deleting recipe:', err);
    }
  }, [loadRecipes, paginationData.page, paginationData.per_page]);

  const rateRecipe = useCallback(async (recipeId, rating) => {
    try {
      const updatedRecipe = await recipeAPI.rateRecipe(recipeId, rating);
      
      // Update recipe in local state
      setRecipes(prevRecipes => 
        prevRecipes.map(recipe => 
          recipe.id === recipeId 
            ? { ...recipe, rating: updatedRecipe.rating }
            : recipe
        )
      );
      
      return updatedRecipe;
    } catch (err) {
      setError(err.userMessage || err.message);
      console.error('Error rating recipe:', err);
    }
  }, []);

  const createRecipe = useCallback(async (recipeData) => {
    try {
      setLoading(true);
      setError(null);
      const newRecipe = await recipeAPI.createRecipe(recipeData);
      
      // Reload first page to show the new recipe
      loadRecipes(1, paginationData.per_page);
      
      return newRecipe;
    } catch (err) {
      setError(err.userMessage || err.message);
      console.error('Error creating recipe:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [loadRecipes, paginationData.per_page]);

  const refreshRecipes = useCallback(() => {
    loadRecipes(paginationData.page, paginationData.per_page);
  }, [loadRecipes, paginationData.page, paginationData.per_page]);

  return {
    recipes,
    loading,
    error,
    pagination: paginationData,
    generateRecipes,
    deleteRecipe,
    rateRecipe,
    createRecipe,
    refreshRecipes,
    loadRecipes,
    searchRecipes
  };
};
