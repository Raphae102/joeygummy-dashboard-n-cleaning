import pandas as pd

class DataCleaner:
    def __init__(self):
        self.df = None

    def set_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Set the dataframe for cleaning.

        Parameters:
        - df: Input dataframe.

        Returns:
        - Updated dataframe after setting the data.
        """
        self.df = df
        return self.df

    def delete_columns_interactively(self, columns_to_delete: list) -> pd.DataFrame:
        """
        Delete specified columns from the dataframe.

        Parameters:
        - columns_to_delete: List of column names to delete from the dataframe.

        Returns:
        - Updated dataframe after deleting specified columns.
        """
        if self.df is None:
            raise ValueError("DataFrame is not initialized. Please call set_data method first.")

        valid_columns = [col for col in columns_to_delete if col in self.df.columns]
        self.df = self.df.drop(columns=valid_columns, axis=1)
        return self.df

    def delete_rows_by_keyword(self, keywords: list) -> pd.DataFrame:
        """
        Delete rows containing specified keywords from the dataframe.

        Parameters:
        - keywords: List of keywords to search for in rows.

        Returns:
        - Updated dataframe after deleting rows with specified keywords.
        """
        if self.df is None:
            raise ValueError("DataFrame is not initialized. Please call set_data method first.")

        keywords = [keyword.lower() for keyword in keywords]
        mask = self.df.apply(lambda row: any(keyword in str(row.values).lower() for keyword in keywords), axis=1)
        self.df = self.df[~mask]
        return self.df

    def extract_integers_from_string(self, columns: list) -> pd.DataFrame:
        """
        Extract integers from string columns in the dataframe.

        Parameters:
        - columns: List of column names containing strings to extract integers from.

        Returns:
        - Updated dataframe with extracted integers in specified columns.
        """
        if self.df is None:
            raise ValueError("DataFrame is not initialized. Please call set_data method first.")

        for col in columns:
            self.df[col] = self.df[col].astype(str).str.extract(r'(\d+)', expand=False)
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        return self.df

    def delete_first_n_rows(self, n: int) -> pd.DataFrame:
        """
        Delete the first N rows from the dataframe.

        Parameters:
        - n: Number of rows to delete.

        Returns:
        - Updated dataframe after deleting the first N rows.
        """
        if self.df is None:
            raise ValueError("DataFrame is not initialized. Please call set_data method first.")

        self.df = self.df.iloc[n:]
        return self.df

    def delete_last_n_rows(self, n: int) -> pd.DataFrame:
        """
        Delete the last N rows from the dataframe.

        Parameters:
        - n: Number of rows to delete.

        Returns:
        - Updated dataframe after deleting the last N rows.
        """
        if self.df is None:
            raise ValueError("DataFrame is not initialized. Please call set_data method first.")

        self.df = self.df.iloc[:-n]
        return self.df
