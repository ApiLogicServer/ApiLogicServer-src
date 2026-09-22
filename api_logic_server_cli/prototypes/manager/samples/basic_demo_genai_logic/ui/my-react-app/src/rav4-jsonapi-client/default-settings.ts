import { safrsErrorHandler, HttpErrorHandler } from './errors';
import { includeRelations } from './ra-jsonapi-client';

export const defaultSettings: settings = {
  total: 'total',
  headers: {
    Accept: 'application/vnd.api+json; charset=utf-8',
    'Content-Type': 'application/vnd.api+json; charset=utf-8'
  },
  updateMethod: 'PATCH',
  arrayFormat: 'brackets',
  includeRelations: [],
  errorHandler: safrsErrorHandler,
  endpointToTypeStripLastLetters: ['Model', 's'] // update/create type: UserModel -> User, Users -> User
};

interface settings {
  total: string;
  headers: {};
  updateMethod: string;
  arrayFormat: string;
  includeRelations: includeRelations[];
  errorHandler: HttpErrorHandler;
  endpointToTypeStripLastLetters?: string[];
}
