import { HttpError, useNotify } from "react-admin";

export class NotImplementedError extends Error {
  constructor(message: string) {
    super(message);
    this.message = message;
    this.name = "NotImplementedError";
  }
}

export class SafrsHttpError extends HttpError {
  constructor(message: string, status: number, body: any) {
    super(message, status, body);
    this.name = "SafrsHttpError";
  }
}

export const safrsErrorHandler: HttpErrorHandler = (
  httpError: HttpError
): HttpError => {
  /* Example Safrs Error message
  {
    "errors": [
      {
        "title": "Request forbidden -- authorization will not help",
        "detail": "",
        "code": "403"
      }
    ]
  } */
  interface err {
    title?: string;
    detail?: string;
    code?: string;
  }

  /*
  Example Safrs Error message
  {"errors": [
    {
    "title": "Generic Error: Invalid Relationship 'REL'", 
    "detail": "Generic Error: Invalid Relationship 'REL'",
    "code": "400"}]
  }
  */

  const errors: { errors: err[] } = httpError.body || httpError.message?.body; // JSON.parse(httpError.body.stringify);
  console.warn("safrsErrorHandler", httpError)
  console.warn("safrsErrorHandler errors", errors)
  console.warn("safrsErrorHandler body, status", httpError.body, httpError.status);
  console.warn("safrsErrorHandler2", errors);
  if (errors?.errors?.length > 0) {
    console.warn(`Data error  ${errors.errors[0].title}`);
    
    return new SafrsHttpError(
      errors.errors[0].title || errors.errors[0].detail || "Unknown Error",
      httpError.status,
      errors.errors[0].code
    );
  }

  console.log("safrsErrorHandler - not a safrs error", errors);
  
  if(httpError.status === 403){
    return new SafrsHttpError(
      "Request forbidden -- authorization will not help",
      httpError.status,
      ""
    )
  }
  
  if(httpError.status === 422 || httpError.status === 422){
    // Change 422 to 403 to prevent the make react-admin redirect to the login page
    return new SafrsHttpError(
      "422 - Request forbidden -- auth error " +JSON.stringify(httpError.body),
      403,
      ""
    )
  }
  
  if(httpError.status === 401){
    // Change 422 to 403 to prevent the make react-admin redirect to the login page
    return new SafrsHttpError(
      "401 - Unauthorized " +JSON.stringify(httpError.body),
      401,
      ""
    )
  }
  
  if(httpError.status === 600){
    // Custom WG error message when the backend is starting up but not ready yet
    return new SafrsHttpError(
      httpError.body.message,
      600,
      httpError.body
    )
  }
  
  if(httpError.body){
    return new SafrsHttpError(
      httpError.body.message,
      httpError.status,
      httpError.body
    )
  }
  
  return new SafrsHttpError(
    "Unknown Error..",
    httpError.status,
    "")

};

export interface HttpErrorHandler {
  (httpError: HttpError): HttpError;
}
