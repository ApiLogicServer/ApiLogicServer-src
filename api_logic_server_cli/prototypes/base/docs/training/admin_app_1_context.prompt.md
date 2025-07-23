
Generate a full React Admin application using the following instructions.  
The result must be a runnable React app (`npm start`) that connects to the supplied JSON:API, with fully implemented components (no placeholders or empty files).

## Critical Data Access Provider Configuration

This project uses a **pre-configured JSON:API data provider** that was built when the project was created. 

### Key Requirements:

1. **Data Provider**: Use the existing `jsonapiClient` from `./rav4-jsonapi-client/ra-jsonapi-client`
2. **Record Context**: For custom components (like cards), ALWAYS wrap with `<RecordContextProvider value={record}>` 
3. **List Data Access**: Use `useListContext()` to get data and loading state
4. **Individual Records**: Use `useRecordContext()` to access record data within providers
5. **API Root**: The data provider connects to `conf.api_root` (typically `http://localhost:5656/api`)

### Example Pattern for Custom List Views:
```javascript
import { useListContext, RecordContextProvider, useRecordContext } from 'react-admin';

const CustomGrid = () => {
    const { data, isLoading } = useListContext();
    
    return (
        <Grid container>
            {data?.map(record => (
                <Grid item key={record.id}>
                    <RecordContextProvider value={record}>
                        <CustomCard />
                    </RecordContextProvider>
                </Grid>
            ))}
        </Grid>
    );
};

const CustomCard = () => {
    const record = useRecordContext();
    return <Card>{record.name}</Card>;
};
```

### CRITICAL: Do NOT create new data providers or modify the existing JSON:API client configuration. The project's data flow depends on the pre-built provider.
